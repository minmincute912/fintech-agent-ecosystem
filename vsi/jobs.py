"""Bot job queue, daily cap, update offset (SQLite) and the run lock shared with `vsi analyze`."""

from __future__ import annotations

import fcntl
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from vsi.news import VN_TZ

_COLUMNS = ("id, chat_id, ticker, date, status, created_at, started_at, finished_at, error, report_path, "
            "rating, summary")


class Refused(Exception):
    """A request the bot will not queue; the message is the Vietnamese reply."""


@dataclass
class Job:
    id: int
    chat_id: int
    ticker: str
    date: str
    status: str  # queued | running | done_unsent | done | failed
    created_at: str
    started_at: str | None
    finished_at: str | None
    error: str | None
    report_path: str | None
    rating: str | None
    summary: str | None


def _utc(now: datetime) -> str:
    return now.astimezone(timezone.utc).isoformat()


class JobStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS jobs (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id INTEGER,"
                       " ticker TEXT, date TEXT, status TEXT, created_at TEXT, started_at TEXT, finished_at TEXT,"
                       " error TEXT, report_path TEXT, rating TEXT, summary TEXT)")
            db.execute("CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT)")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path, timeout=30)
        try:
            with db:
                yield db
        finally:
            db.close()

    def _jobs(self, where: str, args=()) -> list[Job]:
        with self._db() as db:
            rows = db.execute(f"SELECT {_COLUMNS} FROM jobs WHERE {where} ORDER BY id", args).fetchall()
        return [Job(*r) for r in rows]

    def get(self, job_id: int) -> Job | None:
        found = self._jobs("id = ?", (job_id,))
        return found[0] if found else None

    def active(self) -> list[Job]:
        return self._jobs("status IN ('queued', 'running')")

    def unsent(self) -> list[Job]:
        return self._jobs("status = 'done_unsent'")

    def next_queued(self) -> Job | None:
        queued = self._jobs("status = 'queued'")
        return queued[0] if queued else None

    def runs_today(self, now: datetime) -> int:
        """Jobs started on the Vietnam calendar day of `now`, plus jobs still queued."""
        today = now.astimezone(VN_TZ).date()
        started = [j for j in self._jobs("started_at IS NOT NULL")
                   if datetime.fromisoformat(j.started_at).astimezone(VN_TZ).date() == today]
        return len(started) + len(self._jobs("status = 'queued'"))

    def enqueue(self, chat_id: int, ticker: str, date: str, cap: int, now: datetime) -> tuple[Job, int]:
        active = self.active()
        if any(j.ticker == ticker and j.date == date for j in active):
            raise Refused(f"{ticker} ngày {date} đã có trong hàng đợi.")
        if self.runs_today(now) >= cap:
            raise Refused(f"Đã đạt giới hạn {cap} lượt phân tích hôm nay; thử lại ngày mai.")
        with self._db() as db:
            cur = db.execute("INSERT INTO jobs (chat_id, ticker, date, status, created_at) VALUES (?, ?, ?, 'queued', ?)",
                             (chat_id, ticker, date, _utc(now)))
            job_id = cur.lastrowid
        return self.get(job_id), len(active) + 1

    def claim(self, job_id: int, now: datetime) -> bool:
        """queued -> running atomically; False if another worker already took it."""
        with self._db() as db:
            cur = db.execute("UPDATE jobs SET status = 'running', started_at = ? WHERE id = ? AND status = 'queued'",
                             (_utc(now), job_id))
            return cur.rowcount == 1

    def start(self, job_id: int, now: datetime) -> None:
        with self._db() as db:
            db.execute("UPDATE jobs SET status = 'running', started_at = ? WHERE id = ?", (_utc(now), job_id))

    def finish(self, job_id: int, status: str, now: datetime, *, error=None, report_path=None, rating=None,
               summary=None) -> None:
        with self._db() as db:
            db.execute("UPDATE jobs SET status = ?, finished_at = ?, error = COALESCE(?, error),"
                       " report_path = COALESCE(?, report_path), rating = COALESCE(?, rating),"
                       " summary = COALESCE(?, summary) WHERE id = ?",
                       (status, _utc(now), error, report_path, rating, summary, job_id))

    def recover(self, now: datetime) -> list[Job]:
        """Jobs a crash left running become failed; they are not re-run (a re-run costs money)."""
        running = self._jobs("status = 'running'")
        for job in running:
            self.finish(job.id, "failed", now, error="bot restarted during the run")
        return running

    def get_state(self, key: str) -> str | None:
        with self._db() as db:
            row = db.execute("SELECT value FROM state WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def set_state(self, key: str, value: str) -> None:
        with self._db() as db:
            db.execute("INSERT INTO state (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                       (key, value))


@contextmanager
def run_lock(path: Path):
    """One paid analysis at a time across processes (bot worker and shell `vsi analyze`)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def instance_lock(path: Path):
    """Non-blocking lock held for the bot's lifetime; None if another bot already holds it."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "a")
    try:
        fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        f.close()
        return None
    return f
