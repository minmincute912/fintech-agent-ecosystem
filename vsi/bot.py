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

from vsi.jobs import JobStore, Refused, run_lock
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
                if day > now.astimezone(VN_TZ).date():
                    return "Ngày phân tích không được ở tương lai."
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
            self.jobs.start(job.id, self.now())
            try:
                result = self.analyze(job.ticker, job.date)
                state = result["final_state"]
                summary = build_summary(job.ticker, job.date, self.facts(job.ticker, job.date),
                                        self.quarter(job.ticker, job.date), self.news_since(),
                                        state.get("final_trade_decision", ""), state.get("trader_investment_plan", ""))
            except Exception as e:  # any failure is reported to the owner, minus secrets
                error = redact(f"{type(e).__name__}: {e}", self.secrets)[:500]
                self.jobs.finish(job.id, "failed", self.now(), error=error)
                log.warning("job %s failed: %s", job.id, error)
                return [Reply(job.chat_id, f"Phân tích {job.ticker} ngày {_d(job.date)} lỗi: {error}")]
        self.jobs.finish(job.id, "done_unsent", self.now(), report_path=result["report_path"],
                         rating=result.get("rating"), summary=summary)
        return self._result_replies(self.jobs.get(job.id))


def _default_analyze(ticker: str, analysis_date: str) -> dict:
    from vsi.cli import analyze
    return analyze(ticker, analysis_date)


def _default_history() -> list[dict]:
    from tradingagents.memory import TradingMemoryLog

    from vsi.markets import vn_config
    return TradingMemoryLog(vn_config()).load_entries()
