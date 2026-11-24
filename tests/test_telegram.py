import json
import logging

import pytest
import requests

from vsi.telegram import Telegram, TelegramError, redact, split_text

TOKEN = "123:SECRET-token"


class Resp:
    def __init__(self, status, body):
        self.status_code, self._body = status, body

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class Session:
    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def ok(result=True):
    return Resp(200, {"ok": True, "result": result})


def test_get_updates_params():
    s = Session(ok([{"update_id": 5}]))
    assert Telegram(TOKEN, s).get_updates(41) == [{"update_id": 5}]
    url, kw = s.calls[0]
    assert url.endswith("/getUpdates")
    assert kw["data"]["offset"] == 41 and kw["data"]["timeout"] == 50
    assert kw["data"]["allowed_updates"] == '["message"]'
    assert kw["timeout"] > 50


def test_send_message_plain_text():
    s = Session(ok(), ok(), ok())
    Telegram(TOKEN, s).send_message(7, "\n".join(["x" * 2999] * 3))
    assert len(s.calls) == 3
    url, kw = s.calls[0]
    assert url.endswith("/sendMessage") and kw["data"]["chat_id"] == 7
    assert "parse_mode" not in kw["data"]


def test_send_document_multipart(tmp_path):
    f = tmp_path / "complete_report.html"
    f.write_text("<html></html>")
    s = Session(ok())
    Telegram(TOKEN, s).send_document(7, f, caption="VNM")
    url, kw = s.calls[0]
    assert url.endswith("/sendDocument") and "document" in kw["files"]
    assert kw["data"] == {"chat_id": 7, "caption": "VNM"}


def test_429_waits_retry_after():
    waits = []
    s = Session(Resp(429, {"ok": False, "description": "Too Many Requests",
                           "parameters": {"retry_after": 7}}), ok())
    Telegram(TOKEN, s, sleep=waits.append).send_message(7, "hi")
    assert waits == [7] and len(s.calls) == 2


@pytest.mark.parametrize("answer", [
    requests.ConnectionError(f"Max retries exceeded with url: https://api.telegram.org/bot{TOKEN}/getUpdates"),
    Resp(401, {"ok": False, "description": f"Unauthorized for bot{TOKEN}"}),
    Resp(500, ValueError("not json")),
    Resp(200, {"ok": False, "description": "Bad Request: chat not found"}),
])
def test_errors_never_contain_token(answer, caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(TelegramError) as e:
        Telegram(TOKEN, Session(answer)).get_updates(None)
    for text in (str(e.value), repr(e.value), json.dumps(vars(e.value), default=str)):
        assert "SECRET" not in text
    assert e.value.__context__ is None and e.value.__cause__ is None
    assert all("SECRET" not in r.getMessage() for r in caplog.records)


def test_split_text():
    text = "a\n" + "b" * 5000 + "\n" + "c" * 10
    chunks = split_text(text, 4096)
    assert all(len(c) <= 4096 for c in chunks)
    assert "".join(chunks).replace("\n", "") == text.replace("\n", "")
    assert split_text("short") == ["short"]
    assert split_text("") == []


def test_redact():
    assert redact("a 123:SECRET-token b", [TOKEN, ""]) == "a *** b"
