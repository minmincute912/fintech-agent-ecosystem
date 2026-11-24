import logging
from datetime import date, datetime

import pandas as pd
import pytest
from tradingagents.dataflows.errors import VendorUnavailableError

from vsi import bot as botmod
from vsi.bot import HELP, Bot, Reply, latest_session
from vsi.jobs import JobStore
from vsi.news import VN_TZ
from vsi.summary import MarketFacts

OWNER = 111


def at(day, hh=10, mm=0):
    return datetime(2026, 11, day, hh, mm, tzinfo=VN_TZ)


class FakeDnse:
    def __init__(self, last_day=25, down=False):
        self.last_day, self.down = last_day, down

    def instrument(self, symbol):
        if self.down:
            raise VendorUnavailableError("DNSE down")
        return {"name": "CTCP Sữa Việt Nam", "market": "HOSE"} if symbol in ("VNM", "FPT") else None

    def daily_ohlc(self, symbol, start, end):
        if self.down:
            raise VendorUnavailableError("DNSE down")
        days = pd.to_datetime([f"2026-11-{d:02d}" for d in (19, 20, 23, 24, 25) if d <= self.last_day])
        return pd.DataFrame({"Date": days, "Close": 52.3})


def msg(text, chat=OWNER, key="message"):
    return {"update_id": 1, key: {"message_id": 9, "chat": {"id": chat, "type": "private"}, "text": text}}


@pytest.fixture
def make(tmp_path):
    def build(now=at(25), client=None, analyze=None, history=()):
        jobs = JobStore(tmp_path / "bot.sqlite")
        b = Bot(allowed={OWNER}, jobs=jobs, client=client or FakeDnse(), cap=10,
                analyze=analyze or (lambda t, d: {}), history=lambda: list(history),
                news_since=lambda: date(2026, 11, 25), now=lambda: now, lock_path=tmp_path / "run.lock",
                facts=lambda t, d: MarketFacts("HOSE", date(2026, 11, 23), 52.3, 50.0, 56.0),
                quarter=lambda t, d: (date(2026, 9, 30), date(2026, 10, 30)), secrets=["123:SECRET-token"])
        return b, jobs
    return build


def texts(replies):
    return [r.text for r in replies]


def test_non_allowlisted_chat_gets_nothing(make, caplog):
    b, jobs = make()
    caplog.set_level(logging.INFO)
    assert b.handle(msg("/analyze VNM bí mật", chat=999)) == []
    assert b.handle(msg("/help", chat=999, key="edited_message")) == []
    assert b.handle(msg("/help", chat=-100123)) == []  # a group
    assert jobs.active() == []
    logged = " ".join(r.getMessage() for r in caplog.records)
    assert "999" in logged and "bí mật" not in logged and "analyze" not in logged


def test_latest_session_drops_today_before_close():
    assert latest_session(FakeDnse(), "VNM", at(25, 10)) == date(2026, 11, 24)
    assert latest_session(FakeDnse(), "VNM", at(25, 15, 30)) == date(2026, 11, 25)
    assert latest_session(FakeDnse(last_day=24), "VNM", at(25, 10)) == date(2026, 11, 24)


def test_analyze_queues_with_default_date(make):
    b, jobs = make(now=at(25, 15, 30))
    assert texts(b.handle(msg("/analyze vnm"))) == ["Đã xếp hàng VNM ngày 25/11/2026, vị trí 1."]
    [job] = jobs.active()
    assert (job.ticker, job.date, job.chat_id) == ("VNM", "2026-11-25", OWNER)


@pytest.mark.parametrize("text", ["/analyze", "/analyze ../x", "/analyze ZZZ", "/analyze VNM 2026-13-01",
                                  "/analyze VNM 2026-12-01", "/analyze VNM hôm qua"])
def test_analyze_rejects_bad_input(make, text):
    b, jobs = make()
    [reply] = b.handle(msg(text))
    assert reply.chat_id == OWNER and reply.text and not reply.document
    assert jobs.active() == []


def test_analyze_accepts_variants(make):
    b, jobs = make()
    b.handle(msg("/ANALYZE VNM 2026-11-20"))
    b.handle(msg("/analyze@SomeBot FPT"))
    assert [(j.ticker, j.date) for j in jobs.active()] == [("VNM", "2026-11-20"), ("FPT", "2026-11-24")]


def test_message_without_text_gets_help(make):
    b, _ = make()
    update = {"update_id": 2, "message": {"chat": {"id": OWNER}, "photo": [{}]}}
    assert texts(b.handle(update)) == [HELP]


def test_dnse_down_when_validating(make):
    b, jobs = make(client=FakeDnse(down=True))
    assert texts(b.handle(msg("/analyze VNM"))) == ["Không kiểm tra được mã lúc này, thử lại sau."]
    assert jobs.active() == []


def test_cap_reply(make, tmp_path):
    b, jobs = make()
    b.cap = 1
    b.handle(msg("/analyze VNM"))
    assert "giới hạn 1" in b.handle(msg("/analyze FPT"))[0].text


def test_status_reply(make):
    b, jobs = make()
    b.handle(msg("/analyze VNM"))
    b.handle(msg("/analyze FPT"))
    jobs.start(jobs.next_queued().id, at(25, 10, 5))
    text = b.handle(msg("/status"))[0].text
    assert "Đang chạy: VNM 24/11/2026" in text and "Đang chờ: 1" in text
    assert "Hôm nay: 2/10 lượt" in text and "Tin tức thu từ: 25/11/2026" in text


def test_history_reply(make):
    entries = [{"date": "2026-11-20", "ticker": "VNM.VN", "rating": "Hold", "pending": False, "raw": "+3.1%",
                "alpha": "+1.2%", "holding": "5d"},
               {"date": "2026-11-23", "ticker": "VNM.VN", "rating": "Underweight", "pending": True, "raw": None,
                "alpha": None, "holding": None},
               {"date": "2026-11-23", "ticker": "SHS.VN", "rating": "Sell", "pending": True, "raw": None,
                "alpha": None, "holding": None}]
    b, _ = make(history=entries)
    text = b.handle(msg("/history vnm"))[0].text
    lines = [line for line in text.splitlines() if "/2026" in line]
    assert lines == ["23/11/2026 · Underweight · chưa có kết quả",
                     "20/11/2026 · Hold · lợi nhuận +3.1% · so với VN-Index +1.2% · 5d"]
    assert "chưa có lịch sử" in b.handle(msg("/history FPT"))[0].text


def test_free_text_gets_help(make):
    b, _ = make()
    assert texts(b.handle(msg("tại sao bearish?"))) == [HELP]
    assert texts(b.handle(msg("/help"))) == [HELP]


DECISION = "**Rating**: Underweight\n\n**Executive Summary**: Giảm tỷ trọng.\n\n**Price Target**: not provided"


def _result(tmp_path):
    report = tmp_path / "rep" / "complete_report.md"
    report.parent.mkdir(exist_ok=True)
    report.write_text("md")
    (report.parent / "complete_report.html").write_text("<html/>")
    return {"rating": "Underweight", "report_path": str(report),
            "final_state": {"final_trade_decision": DECISION, "trader_investment_plan": "**Stop Loss**: 49.8"}}


def test_work_once_sends_summary_and_document(make, tmp_path):
    b, jobs = make(analyze=lambda t, d: _result(tmp_path))
    b.handle(msg("/analyze VNM"))
    replies = b.work_once()
    assert replies[0].text.startswith("VNM (HOSE) · phân tích ngày 24/11/2026") and "Cắt lỗ: 49,80" in replies[0].text
    assert replies[1].document == tmp_path / "rep" / "complete_report.html" and replies[1].job_id
    job = jobs.get(replies[1].job_id)
    assert job.status == "done_unsent" and job.rating == "Underweight"
    assert b.work_once()[-1].job_id == job.id  # still unsent, so sent again until marked sent


def test_work_once_failure_is_reported_without_secrets(make):
    def boom(t, d):
        raise RuntimeError("boom 123:SECRET-token")
    b, jobs = make(analyze=boom)
    b.handle(msg("/analyze VNM"))
    [reply] = b.work_once()
    assert "RuntimeError" in reply.text and "SECRET" not in reply.text
    assert jobs._jobs("1=1")[0].status == "failed"


def test_unsent_report_is_sent_later(make, tmp_path):
    calls = []
    b, jobs = make(analyze=lambda t, d: calls.append(t) or _result(tmp_path))
    b.handle(msg("/analyze VNM"))
    first = b.work_once()  # sending fails, job stays done_unsent
    b.handle(msg("/analyze FPT"))
    again = b.work_once()  # resends VNM before starting FPT
    assert again[0].text == first[0].text and calls == ["VNM"]
    b.mark_sent(again[-1].job_id)
    assert b.work_once()[0].text.startswith("FPT")
    assert calls == ["VNM", "FPT"]


def test_reply_type():
    assert Reply(1, "x").document is None and Reply(1, "x").job_id is None
    assert botmod.HELP.startswith("Lệnh")


# --- runtime (Task 6) ---

import os  # noqa: E402

from vsi.bot import backoff, deliver, poll_once, startup_problems  # noqa: E402
from vsi.telegram import TelegramError  # noqa: E402

GOOD_ENV = {"TELEGRAM_BOT_TOKEN": "123:SECRET-token", "TELEGRAM_ALLOWED_CHAT_IDS": "111, 222",
            "OPENAI_API_KEY": "k", "DNSE_API_KEY": "i", "DNSE_API_SECRET": "s"}


def _env_file(tmp_path, mode):
    f = tmp_path / ".env"
    f.write_text("x=1\n")
    os.chmod(f, mode)
    return f


def test_startup_refuses(tmp_path):
    ok = _env_file(tmp_path, 0o600)
    assert startup_problems(GOOD_ENV, ok) == []
    cases = [({"TELEGRAM_BOT_TOKEN": ""}, "TELEGRAM_BOT_TOKEN"),
             ({"TELEGRAM_ALLOWED_CHAT_IDS": ""}, "TELEGRAM_ALLOWED_CHAT_IDS"),
             ({"TELEGRAM_ALLOWED_CHAT_IDS": "12,abc"}, "TELEGRAM_ALLOWED_CHAT_IDS"),
             ({"OPENAI_API_KEY": ""}, "OPENAI_API_KEY"),
             ({"DNSE_API_SECRET": ""}, "DNSE")]
    for change, name in cases:
        problems = startup_problems(GOOD_ENV | change, ok)
        assert len(problems) == 1 and name in problems[0]
    loose = startup_problems(GOOD_ENV, _env_file(tmp_path, 0o644))
    assert len(loose) == 1 and "chmod 600" in loose[0]
    assert all("SECRET" not in p for p in loose + startup_problems(GOOD_ENV | {"TELEGRAM_ALLOWED_CHAT_IDS": "x"}, ok))


class FakeTelegram:
    def __init__(self, updates=(), fail_send=False):
        self.updates, self.offsets, self.sent, self.fail_send = list(updates), [], [], fail_send

    def get_updates(self, offset, timeout=50):
        self.offsets.append(offset)
        return [u for u in self.updates if offset is None or u["update_id"] >= offset]

    def send_message(self, chat_id, text):
        if self.fail_send:
            raise TelegramError("sendMessage", None, "ConnectionError")
        self.sent.append((chat_id, text))

    def send_document(self, chat_id, path, caption=""):
        if self.fail_send:
            raise TelegramError("sendDocument", None, "ConnectionError")
        self.sent.append((chat_id, path))


def test_update_handled_once_across_restart(make, tmp_path):
    b, jobs = make()
    handled = []

    def handle(update):
        handled.append(update["update_id"])
        raise RuntimeError("crash while handling")

    b.handle = handle
    tg = FakeTelegram([msg("/help") | {"update_id": 41}])
    with pytest.raises(RuntimeError):
        poll_once(b, tg, jobs)
    assert JobStore(tmp_path / "bot.sqlite").get_state("offset") == "42"  # saved before handling
    b2, jobs2 = make()
    poll_once(b2, tg, jobs2)
    assert tg.offsets == [None, 42] and handled == [41]


def test_poll_once_sends_replies(make):
    b, jobs = make()
    tg = FakeTelegram([msg("/help") | {"update_id": 7}])
    poll_once(b, tg, jobs)
    assert tg.sent == [(OWNER, HELP)]


def test_deliver_marks_job_sent_only_after_success(make, tmp_path):
    b, jobs = make(analyze=lambda t, d: _result(tmp_path))
    b.handle(msg("/analyze VNM"))
    replies = b.work_once()
    with pytest.raises(TelegramError):
        deliver(FakeTelegram(fail_send=True), b, replies)
    assert jobs.unsent()
    deliver(FakeTelegram(), b, replies)
    assert jobs.unsent() == [] and jobs.get(replies[-1].job_id).status == "done"


def test_poll_backoff_caps_at_60():
    assert (backoff(0), backoff(1), backoff(3), backoff(10)) == (0, 1, 4, 60)
