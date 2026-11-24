"""Telegram bot commands and the queue worker step (M3). Owner-only, research-only, never trades.

`Bot.handle()` turns one Telegram update into replies; `Bot.work_once()` runs the next queued
analysis. Both are pure enough to test without the network; `run()` wires them to Telegram.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

from tradingagents.dataflows.errors import NoMarketDataError, VendorError

from vsi.jobs import JobStore, Refused, instance_lock, run_lock
from vsi.markets import normalize_ticker
from vsi.news import VN_TZ
from vsi.summary import MarketFacts, build_summary
from vsi.telegram import redact

log = logging.getLogger(__name__)

HELP = (
    "Lệnh:\n"
    "/analyze MÃ [YYYY-MM-DD] — phân tích một mã; mặc định là phiên gần nhất đã có dữ liệu\n"
    "/status — việc đang chạy, hàng đợi, số lượt hôm nay\n"
    "/history MÃ — các lần phân tích trước của mã\n"
    "/help — trợ giúp\n\n"
    "Chỉ để nghiên cứu, không phải lời khuyên đầu tư. Bot không đặt lệnh."
)
_CLOSE = time(15, 5)  # a bar dated today is not trusted as a closed session before this
_SECRET_KEYS = ("TELEGRAM_BOT_TOKEN", "OPENAI_API_KEY", "DNSE_API_KEY", "DNSE_API_SECRET")


@dataclass
class Reply:
    chat_id: int
    text: str | None = None
    document: Path | None = None
    job_id: int | None = None  # set on a job's last reply: the job is marked done once it is sent


def _d(day: date | str) -> str:
    return f"{date.fromisoformat(str(day)):%d/%m/%Y}"


def latest_session(client, base: str, now: datetime) -> date:
    """The ticker's latest DNSE daily bar; a bar dated today counts only after 15:05 Vietnam time."""
    local = now.astimezone(VN_TZ)
    df = client.daily_ohlc(base, local.date() - timedelta(days=20), local.date())
    days = [d.date() for d in df["Date"]] if len(df) else []
    if days and days[-1] == local.date() and local.time() < _CLOSE:
        days = days[:-1]
    if not days:
        raise NoMarketDataError(base, base, "no DNSE bar in the last 20 days")
    return days[-1]


def _market_facts(ticker: str, analysis_date: str) -> MarketFacts:
    from vsi import bridge  # the installed DNSE client and its cached loader
    df = bridge.load_ohlcv(ticker, analysis_date).tail(60)
    info = bridge._client.instrument(ticker) or {}
    return MarketFacts(exchange=info.get("market") or "?", last_bar=df["Date"].iloc[-1].date(),
                       close=float(df["Close"].iloc[-1]), low60=float(df["Low"].min()),
                       high60=float(df["High"].max()))


class Bot:
    def __init__(self, allowed: set[int], jobs: JobStore, client, cap: int, analyze=None, history=None,
                 news_since=None, now=None, lock_path: Path | None = None, facts=None, quarter=None,
                 secrets=None):
        from vsi import fundamentals, news
        self.allowed, self.jobs, self.client, self.cap = allowed, jobs, client, cap
        self.analyze = analyze or _default_analyze
        self.history = history or _default_history
        self.news_since = news_since or (lambda: news.default_store().collected_since())
        self.now = now or (lambda: datetime.now(VN_TZ))
        self.lock_path = lock_path or news.vsi_home() / "run.lock"
        self.facts = facts or _market_facts
        self.quarter = quarter or fundamentals.latest_quarter
        self.secrets = secrets if secrets is not None else [os.environ.get(k, "") for k in _SECRET_KEYS]
        self.refresh = _clear_caches

    # --- commands ------------------------------------------------------------------------

    def handle(self, update: dict) -> list[Reply]:
        message = update.get("message")
        if not message:
            return []  # edited messages, channel posts: not commands
        chat = (message.get("chat") or {}).get("id")
        if chat not in self.allowed:
            log.info("dropped update from chat %s", chat)  # never the content
            return []
        words = (message.get("text") or "").split()
        command = words[0].lower().split("@")[0] if words else ""
        args = words[1:]
        if command == "/analyze":
            return [Reply(chat, self._analyze(chat, args))]
        if command == "/status":
            return [Reply(chat, self._status())]
        if command == "/history":
            return [Reply(chat, self._history(args))]
        return [Reply(chat, HELP)]

    def _analyze(self, chat: int, args: list[str]) -> str:
        if not args or len(args) > 2:
            return "Cú pháp: /analyze MÃ [YYYY-MM-DD], ví dụ /analyze VNM"
        try:
            base = normalize_ticker(args[0]).removesuffix(".VN")
        except ValueError:
            return "Mã không hợp lệ. Mã là 3–10 chữ hoặc số, ví dụ VNM."
        now = self.now()
        try:
            if self.client.instrument(base) is None:
                return f"{base} không niêm yết trên HOSE, HNX hoặc UPCoM."
            if len(args) == 2:
                try:
                    day = date.fromisoformat(args[1])
                except ValueError:
                    return "Ngày không hợp lệ; dùng dạng YYYY-MM-DD, ví dụ 2026-11-20."
                local = now.astimezone(VN_TZ)
                if day > local.date():
                    return "Ngày phân tích không được ở tương lai."
                if day == local.date() and local.time() < _CLOSE:
                    return "Phiên hôm nay chưa đóng cửa; chỉ phân tích ngày hôm nay sau 15:05."
            else:
                day = latest_session(self.client, base, now)
        except NoMarketDataError:
            return f"Không có dữ liệu giá gần đây cho {base}."
        except VendorError:
            return "Không kiểm tra được mã lúc này, thử lại sau."
        try:
            _, position = self.jobs.enqueue(chat, base, day.isoformat(), self.cap, now)
        except Refused as e:
            return str(e)
        return f"Đã xếp hàng {base} ngày {_d(day)}, vị trí {position}."

    def _status(self) -> str:
        active = self.jobs.active()
        running = [j for j in active if j.status == "running"]
        since = self.news_since()
        return "\n".join([
            "Đang chạy: " + (f"{running[0].ticker} {_d(running[0].date)}" if running else "không có"),
            f"Đang chờ: {len(active) - len(running)}",
            f"Hôm nay: {self.jobs.runs_today(self.now())}/{self.cap} lượt",
            "Tin tức thu từ: " + (_d(since) if since else "chưa thu"),
        ])

    def _history(self, args: list[str]) -> str:
        if len(args) != 1:
            return "Cú pháp: /history MÃ, ví dụ /history VNM"
        try:
            symbol = normalize_ticker(args[0])
        except ValueError:
            return "Mã không hợp lệ."
        entries = sorted((e for e in self.history() if e.get("ticker") == symbol),
                         key=lambda e: e["date"], reverse=True)[:10]
        if not entries:
            return f"{symbol.removesuffix('.VN')}: chưa có lịch sử phân tích."
        lines = [f"Lịch sử {symbol.removesuffix('.VN')} (tối đa 10, mới nhất trước; chưa được kiểm chứng):"]
        for e in entries:
            if e.get("pending"):
                lines.append(f"{_d(e['date'])} · {e['rating']} · chưa có kết quả")
            else:
                lines.append(f"{_d(e['date'])} · {e['rating']} · lợi nhuận {e.get('raw') or 'n/a'} · "
                             f"so với VN-Index {e.get('alpha') or 'n/a'} · {e.get('holding') or 'n/a'}")
        return "\n".join(lines)

    # --- worker --------------------------------------------------------------------------

    def _result_replies(self, job) -> list[Reply]:
        report = Path(job.report_path)
        html = report.with_name("complete_report.html")
        return [Reply(job.chat_id, job.summary),
                Reply(job.chat_id, document=html if html.exists() else report, job_id=job.id)]

    def mark_sent(self, job_id: int) -> None:
        self.jobs.finish(job_id, "done", self.now())

    def work_once(self) -> list[Reply]:
        """Re-send one finished-but-unsent report, else run the next queued job. [] when idle."""
        unsent = self.jobs.unsent()
        if unsent:
            return self._result_replies(unsent[0])
        job = self.jobs.next_queued()
        if job is None:
            return []
        with run_lock(self.lock_path):
            if not self.jobs.claim(job.id, self.now()):  # another worker took it while we waited
                return []
            self.refresh()  # a long-running bot must not reuse yesterday's prices or statements
            try:
                result = self.analyze(job.ticker, job.date)
            except Exception as e:  # any failure is reported to the owner, minus secrets
                error = self._redacted(e)
                self.jobs.finish(job.id, "failed", self.now(), error=error)
                log.warning("job %s failed: %s", job.id, error)
                return [Reply(job.chat_id, f"Phân tích {job.ticker} ngày {_d(job.date)} lỗi: {error}")]
        try:  # the paid run succeeded: a summary problem must not lose its report
            state = result["final_state"]
            summary = build_summary(job.ticker, job.date, self.facts(job.ticker, job.date),
                                    self.quarter(job.ticker, job.date), self.news_since(),
                                    state.get("final_trade_decision", ""), state.get("trader_investment_plan", ""))
        except Exception as e:
            summary = (f"{job.ticker} · phân tích ngày {_d(job.date)} · xếp hạng {result.get('rating') or '?'} "
                       f"(chưa được kiểm chứng)\nKhông tạo được tóm tắt: {self._redacted(e)}\n"
                       "Báo cáo đầy đủ: file đính kèm")
        self.jobs.finish(job.id, "done_unsent", self.now(), report_path=result["report_path"],
                         rating=result.get("rating"), summary=summary)
        return self._result_replies(self.jobs.get(job.id))

    def _redacted(self, e: Exception) -> str:
        return redact(f"{type(e).__name__}: {e}", self.secrets)[:500]


def _clear_caches() -> None:
    from vsi import bridge, fundamentals
    bridge.load_ohlcv.cache_clear()
    if fundamentals._client is not None and hasattr(fundamentals._client, "_cache"):
        fundamentals._client._cache.clear()


def _default_analyze(ticker: str, analysis_date: str) -> dict:
    from vsi.cli import analyze
    return analyze(ticker, analysis_date)


def _default_history() -> list[dict]:
    from tradingagents.memory import TradingMemoryLog

    from vsi.markets import vn_config
    return TradingMemoryLog(vn_config()).load_entries()


# --- runtime -------------------------------------------------------------------------------

def startup_problems(env, env_file: Path) -> list[str]:
    """Reasons to refuse to start; never echoes a secret value."""
    problems = []
    if not env.get("TELEGRAM_BOT_TOKEN"):
        problems.append("TELEGRAM_BOT_TOKEN is not set in .env (create the bot with @BotFather)")
    ids = [p.strip() for p in (env.get("TELEGRAM_ALLOWED_CHAT_IDS") or "").split(",") if p.strip()]
    if not ids:
        problems.append("TELEGRAM_ALLOWED_CHAT_IDS is empty; the bot answers only listed chats")
    elif not all(p.lstrip("-").isdigit() for p in ids):
        problems.append("TELEGRAM_ALLOWED_CHAT_IDS must be comma-separated integers")
    if not env.get("OPENAI_API_KEY"):
        problems.append("OPENAI_API_KEY is not set in .env")
    if not env.get("DNSE_API_KEY") or not env.get("DNSE_API_SECRET"):
        problems.append("DNSE_API_KEY and DNSE_API_SECRET must be set in .env")
    if env_file.exists() and env_file.stat().st_mode & 0o077:
        problems.append(".env is readable by group or others; run: chmod 600 .env")
    return problems


def backoff(failures: int) -> float:
    return 0 if failures <= 0 else min(60, 2 ** (failures - 1))


def deliver(telegram, bot: Bot, replies: list[Reply]) -> None:
    """Send replies in order; a job is marked done only after its last reply went out."""
    for r in replies:
        if r.document:
            telegram.send_document(r.chat_id, r.document)
        elif r.text:
            telegram.send_message(r.chat_id, r.text)
        if r.job_id:
            bot.mark_sent(r.job_id)


_PERMANENT = {400, 403, 404, 413}  # Telegram will never accept this send; retrying blocks the queue


def work_and_deliver(bot: Bot, telegram) -> float:
    """One worker step; returns seconds to wait before the next. Never raises."""
    from vsi.telegram import TelegramError
    replies = []
    try:
        replies = bot.work_once()
        if not replies:
            return 5
        deliver(telegram, bot, replies)
        return 0
    except TelegramError as e:
        job_id = next((r.job_id for r in replies if r.job_id), None)
        if job_id and e.status in _PERMANENT:
            bot.jobs.finish(job_id, "done", bot.now(), error=f"not delivered: {e}")
            log.warning("job %s report rejected by Telegram, giving up: %s", job_id, e)
            return 0
        log.warning("sending a result failed, will retry: %s", e)
        return 30
    except Exception:
        log.exception("worker step failed; retrying")
        return 30


def poll_once(bot: Bot, telegram, jobs: JobStore) -> None:
    stored = jobs.get_state("offset")
    updates = telegram.get_updates(int(stored) if stored else None)
    if not updates:
        return
    # saved first: a crash while handling loses that command (re-send it) but never runs it twice
    jobs.set_state("offset", str(max(u["update_id"] for u in updates) + 1))
    for update in updates:
        deliver(telegram, bot, bot.handle(update))


def run() -> int:
    """`vsi bot`: start-up checks, then poll loop (main thread), worker and hourly news threads."""
    import signal
    import threading

    from vsi import news
    from vsi.bridge import install
    from vsi.dnse import DnseClient
    from vsi.telegram import Telegram, TelegramError

    problems = startup_problems(os.environ, Path(".env"))
    if problems:
        for p in problems:
            print(f"error: {p}")
        return 2
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    for noisy in ("urllib3", "requests"):  # keep request lines (and any URL) out of the log by construction
        logging.getLogger(noisy).setLevel(logging.WARNING)

    held = instance_lock(news.vsi_home() / "bot.lock")
    if held is None:
        print("error: another vsi bot is already running with this VSI_HOME")
        return 2
    client = DnseClient.from_env()
    install(client)
    jobs = JobStore(news.vsi_home() / "bot.sqlite")
    allowed = {int(p) for p in os.environ["TELEGRAM_ALLOWED_CHAT_IDS"].split(",") if p.strip()}
    bot = Bot(allowed, jobs, client, int(os.environ.get("VSI_DAILY_RUN_CAP") or 10))
    telegram = Telegram(os.environ["TELEGRAM_BOT_TOKEN"])
    stop = threading.Event()
    signal.signal(signal.SIGTERM, lambda *_: stop.set())
    signal.signal(signal.SIGINT, lambda *_: stop.set())

    for job in jobs.recover(bot.now()):
        try:
            telegram.send_message(job.chat_id, f"Phân tích {job.ticker} ngày {_d(job.date)} bị dừng vì bot khởi động "
                                               "lại; gửi lại /analyze nếu vẫn cần.")
        except TelegramError as e:
            log.warning("could not notify about job %s: %s", job.id, e)

    def worker():
        while not stop.is_set():
            stop.wait(work_and_deliver(bot, telegram))

    def collector():
        while not stop.is_set():
            try:
                result = news.collect(news.default_store())
                log.info("news collected: %d new", sum(n for n in result.values() if isinstance(n, int)))
            except Exception as e:  # a collection failure must not stop the bot
                log.warning("news collection failed: %s", type(e).__name__)
            stop.wait(3600)

    for target in (worker, collector):
        threading.Thread(target=target, daemon=True).start()
    log.info("bot started; allowed chats: %d; daily cap: %d", len(allowed), bot.cap)
    failures = 0
    while not stop.is_set():
        try:
            poll_once(bot, telegram, jobs)
            failures = 0
        except TelegramError as e:
            failures += 1
            hint = " (another bot instance is polling with this token)" if e.status == 409 else ""
            log.warning("polling failed (%d in a row): %s%s", failures, e, hint)
            stop.wait(backoff(failures))
        except Exception:
            failures += 1
            log.exception("unexpected error while handling updates")
            stop.wait(backoff(failures))
    log.info("bot stopped")
    return 0
