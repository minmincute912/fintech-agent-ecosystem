"""Minimal Telegram Bot API client (getUpdates, sendMessage, sendDocument) that never exposes the token.

The Bot API puts the token in the URL path, so the URL is built in one place and never logged,
raised or returned. Errors carry the method, HTTP status and a redacted description only.
"""

from __future__ import annotations

import time
from collections.abc import Iterable
from pathlib import Path

import requests

_API = "https://api.telegram.org/bot{token}/{method}"
_LIMIT = 4096
_RETRIES_429 = 3


class TelegramError(Exception):
    def __init__(self, method: str, status: int | None, description: str):
        super().__init__(f"Telegram {method} failed: {status or 'network'} {description}")
        self.method, self.status, self.description = method, status, description


def redact(text: str, secrets: Iterable[str]) -> str:
    for secret in secrets:
        if secret:
            text = text.replace(secret, "***")
    return text


def split_text(text: str, limit: int = _LIMIT) -> list[str]:
    """Chunks of at most `limit` characters, cut at line ends; an overlong line is cut hard."""
    chunks, current = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            if current:
                chunks.append(current)
                current = ""
            chunks.append(line[:limit])
            line = line[limit:]
        if len(current) + len(line) > limit:
            chunks.append(current)
            current = ""
        current += line
    if current:
        chunks.append(current)
    return [c.rstrip("\n") for c in chunks if c.strip("\n")]  # Telegram rejects empty text


class Telegram:
    def __init__(self, token: str, session=None, sleep=time.sleep):
        self._token = token
        self._session = session or requests.Session()
        self._sleep = sleep

    def _call(self, method: str, *, data: dict, files=None, timeout: float = 30):
        for _ in range(_RETRIES_429 + 1):
            failure = None
            try:
                resp = self._session.post(_API.format(token=self._token, method=method),
                                          data=data, files=files, timeout=timeout)
            except requests.RequestException as e:
                failure = type(e).__name__  # the exception text holds the URL, so only its class is kept
            if failure:  # raised outside the except: no chained exception carries the URL
                raise TelegramError(method, None, failure)
            try:
                body = resp.json()
            except ValueError:
                body = {}
            if resp.status_code == 429:
                self._sleep(int((body.get("parameters") or {}).get("retry_after", 1)))
                continue
            if 200 <= resp.status_code < 300 and body.get("ok"):
                return body.get("result")
            raise TelegramError(method, resp.status_code, redact(str(body.get("description", "")), [self._token]))
        raise TelegramError(method, 429, "still rate-limited after retries")

    def get_updates(self, offset: int | None, timeout: int = 50) -> list[dict]:
        data = {"timeout": timeout, "allowed_updates": '["message"]'}
        if offset is not None:
            data["offset"] = offset
        return self._call("getUpdates", data=data, timeout=timeout + 15) or []

    def send_message(self, chat_id: int, text: str) -> None:
        for chunk in split_text(text):
            self._call("sendMessage", data={"chat_id": chat_id, "text": chunk})

    def send_document(self, chat_id: int, path: Path, caption: str = "") -> None:
        with open(path, "rb") as f:
            self._call("sendDocument", data={"chat_id": chat_id, "caption": caption},
                       files={"document": (Path(path).name, f)}, timeout=120)
