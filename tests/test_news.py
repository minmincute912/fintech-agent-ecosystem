from datetime import date, datetime, timezone
from pathlib import Path

from vsi import news
from vsi.news import NewsItem, NewsStore, parse_feed

FIXTURE = (Path(__file__).parent / "fixtures" / "rss_sample.xml").read_bytes()


def _item(title, published, link=None, description="", outlet="VnExpress"):
    return NewsItem(title=title, description=description, link=link or f"https://example.vn/{title}",
                    outlet=outlet, published=published)


def test_parse_feed_reads_items():
    items = parse_feed(FIXTURE, "VnExpress")
    first = items[0]
    assert first.title == "VNM: lãi quý 3 tăng 5%"
    assert first.link == "https://example.vn/vnm-lai-quy-3.html"
    assert first.outlet == "VnExpress"
    assert first.published == datetime(2026, 11, 24, 10, 7, tzinfo=timezone.utc)


def test_parse_feed_skips_bad_items():
    items = parse_feed(FIXTURE, "CafeF")
    assert [i.link for i in items] == ["https://example.vn/vnm-lai-quy-3.html", "https://example.vn/thi-truong.html"]
    assert items[1].description == "VN-Index tăng & thanh khoản cải thiện"
    assert items[1].title == "Thị trường chứng khoán & dòng tiền"
    assert parse_feed(b"<rss><channel><item>", "CafeF") == []
    assert parse_feed(b"", "CafeF") == []


def test_store_dedupes_on_link(tmp_path):
    store = NewsStore(tmp_path / "news.sqlite")
    items = parse_feed(FIXTURE, "VnExpress") + [_item("x", datetime(2026, 11, 20, tzinfo=timezone.utc))]
    assert store.add(items) == 3
    assert store.add(items) == 0


def test_between_uses_vietnam_dates(tmp_path):
    store = NewsStore(tmp_path / "news.sqlite")
    store.add([_item("late", datetime(2026, 11, 23, 17, 30, tzinfo=timezone.utc))])  # 00:30 on 24/11 in Vietnam
    assert [i.title for i in store.between(date(2026, 11, 24), date(2026, 11, 24))] == ["late"]
    assert store.between(date(2026, 11, 23), date(2026, 11, 23)) == []


def test_between_newest_first_and_roundtrip(tmp_path):
    store = NewsStore(tmp_path / "news.sqlite")
    a = _item("a", datetime(2026, 11, 20, 1, tzinfo=timezone.utc), description="d")
    b = _item("b", datetime(2026, 11, 21, 1, tzinfo=timezone.utc))
    store.add([a, b])
    assert store.between(date(2026, 11, 1), date(2026, 11, 30)) == [b, a]


def test_default_store_uses_vsi_home(tmp_path, monkeypatch):
    monkeypatch.setenv("VSI_HOME", str(tmp_path / "home"))
    assert news.default_store().path == tmp_path / "home" / "news.sqlite"


class FakeResponse:
    def __init__(self, content, status_code=200):
        self.content, self.status_code = content, status_code


class FakeSession:
    def __init__(self, answers):
        self.answers, self.urls = answers, []

    def get(self, url, **kwargs):
        self.urls.append(url)
        answer = self.answers.get(url, FakeResponse(b"", 404))
        if isinstance(answer, Exception):
            raise answer
        return answer


def test_feeds_are_the_nine_planned():
    assert len(news.FEEDS) == 9
    assert {outlet for outlet, _ in news.FEEDS} == {"VnExpress", "VnEconomy", "Báo Đầu tư", "Tuổi Trẻ", "CafeF", "Vietstock"}
    assert all(url.startswith("https://") for _, url in news.FEEDS)


def test_collect_continues_when_a_feed_fails(tmp_path, monkeypatch):
    import requests
    feeds = (("A", "https://a.vn/rss"), ("B", "https://b.vn/rss"), ("C", "https://c.vn/rss"))
    monkeypatch.setattr(news, "FEEDS", feeds)
    session = FakeSession({"https://a.vn/rss": requests.ConnectionError("down"),
                           "https://b.vn/rss": FakeResponse(FIXTURE)})
    store = NewsStore(tmp_path / "news.sqlite")
    result = news.collect(store, session=session)
    assert result == {"A https://a.vn/rss": "ConnectionError", "B https://b.vn/rss": 2, "C https://c.vn/rss": "HTTP 404"}
    assert len(store.between(date(2026, 1, 1), date(2026, 12, 31))) == 2
