"""Vietnamese business news from free RSS feeds, kept in a local SQLite store.

Outlets allow free reading by individuals, not republishing: only title, summary, link,
outlet and time are stored, and news text reaches the agents as quoted, untrusted material.
"""

from __future__ import annotations

import html
import os
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree
from zoneinfo import ZoneInfo

import requests

VN_TZ = ZoneInfo("Asia/Ho_Chi_Minh")


@dataclass(frozen=True)
class NewsItem:
    title: str
    description: str
    link: str
    outlet: str
    published: datetime  # tz-aware UTC


def _clean(text: str | None) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    return " ".join(text.split())


def _published(raw: str | None) -> datetime | None:
    try:
        dt = parsedate_to_datetime(raw.strip())
    except (AttributeError, TypeError, ValueError, IndexError):
        return None
    if dt.tzinfo is None:  # a feed without an offset: Vietnamese outlets publish in Vietnam time
        dt = dt.replace(tzinfo=VN_TZ)
    return dt.astimezone(timezone.utc)


def parse_feed(xml: bytes, outlet: str) -> list[NewsItem]:
    """Items with a title, link and readable pubDate; anything else is skipped, never raised."""
    try:
        root = ElementTree.fromstring(xml)
    except ElementTree.ParseError:
        return []
    items = []
    for node in root.iter("item"):
        title, link = _clean(node.findtext("title")), (node.findtext("link") or "").strip()
        published = _published(node.findtext("pubDate"))
        if title and link and published:
            items.append(NewsItem(title, _clean(node.findtext("description")), link, outlet, published))
    return items


class NewsStore:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._db() as db:
            db.execute("CREATE TABLE IF NOT EXISTS news (link TEXT PRIMARY KEY, title TEXT, description TEXT,"
                       " outlet TEXT, published TEXT, fetched_at TEXT)")

    @contextmanager
    def _db(self):
        db = sqlite3.connect(self.path)
        try:
            with db:  # commit on success, roll back on error
                yield db
        finally:
            db.close()

    def add(self, items: list[NewsItem]) -> int:
        fetched = datetime.now(timezone.utc).isoformat()
        rows = [(i.link, i.title, i.description, i.outlet, i.published.isoformat(), fetched) for i in items]
        with self._db() as db:
            before = db.total_changes
            db.executemany("INSERT OR IGNORE INTO news VALUES (?, ?, ?, ?, ?, ?)", rows)
            return db.total_changes - before

    def between(self, start: date, end: date) -> list[NewsItem]:
        """Items whose Vietnam-time publication date is in [start, end], newest first."""
        lo = datetime.combine(start, time(), VN_TZ).astimezone(timezone.utc).isoformat()
        hi = datetime.combine(end + timedelta(days=1), time(), VN_TZ).astimezone(timezone.utc).isoformat()
        with self._db() as db:
            rows = db.execute("SELECT title, description, link, outlet, published FROM news"
                              " WHERE published >= ? AND published < ? ORDER BY published DESC", (lo, hi)).fetchall()
        return [NewsItem(t, d, link, o, datetime.fromisoformat(p)) for t, d, link, o, p in rows]


def default_store() -> NewsStore:
    home = Path(os.environ.get("VSI_HOME") or Path.home() / ".tradingagents" / "vsi")
    return NewsStore(home / "news.sqlite")


FEEDS = (
    ("VnExpress", "https://vnexpress.net/rss/kinh-doanh.rss"),
    ("VnEconomy", "https://vneconomy.vn/chung-khoan.rss"),
    ("VnEconomy", "https://vneconomy.vn/nhip-cau-doanh-nghiep.rss"),
    ("Báo Đầu tư", "https://baodautu.vn/kinh-doanh.rss"),
    ("Báo Đầu tư", "https://baodautu.vn/thong-tin-doanh-nghiep.rss"),
    ("Tuổi Trẻ", "https://tuoitre.vn/kinh-doanh.rss"),
    ("CafeF", "https://cafef.vn/thi-truong-chung-khoan.rss"),
    ("CafeF", "https://cafef.vn/doanh-nghiep.rss"),
    ("Vietstock", "https://vietstock.vn/830/chung-khoan/co-phieu.rss"),
)
_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; vsi-news/0.1; personal research)"}


def collect(store: NewsStore, session=None) -> dict[str, int | str]:
    """Fetch every feed once; '<outlet> <url>' -> new rows, or why that feed failed. One bad feed never stops the rest."""
    session = session or requests.Session()
    result: dict[str, int | str] = {}
    for outlet, url in FEEDS:
        key = f"{outlet} {url}"
        try:
            r = session.get(url, headers=_HEADERS, timeout=20)
        except requests.RequestException as e:
            result[key] = type(e).__name__
            continue
        if not 200 <= r.status_code < 300:
            result[key] = f"HTTP {r.status_code}"
            continue
        result[key] = store.add(parse_feed(r.content, outlet))
    return result
