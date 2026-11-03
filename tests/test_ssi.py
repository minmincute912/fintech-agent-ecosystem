from datetime import date, timedelta

import pytest
from tradingagents.dataflows.errors import NoMarketDataError, VendorError, VendorNotConfiguredError

from vsi.ssi import SsiClient


class _Resp:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        return self._body


class FakeSession:
    """Replies from a queue of (status_code, json) pairs and records every call."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def post(self, url, json=None, timeout=None):
        self.calls.append({"method": "POST", "url": url, "json": json})
        return _Resp(*self.replies.pop(0))

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"method": "GET", "url": url, "params": dict(params), "headers": dict(headers)})
        return _Resp(*self.replies.pop(0))


TOKEN_OK = (200, {"status": 200, "message": "Success", "data": {"accessToken": "TKN"}})


def ohlc_page(rows):
    return (200, {"status": "Success", "totalRecord": len(rows), "data": rows})


def ROW(d, c):
    return {"Symbol": "VNM", "Market": "HOSE", "TradingDate": d, "Time": None, "Open": str(c),
            "High": str(c + 100), "Low": str(c - 100), "Close": str(c), "Volume": "1000", "Value": "1"}


def test_daily_ohlc_parses_and_sorts():
    s = FakeSession([TOKEN_OK, ohlc_page([ROW("31/10/2026", 56300), ROW("30/10/2026", 56000)])])
    df = SsiClient("id", "secret", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert df["Date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-10-30", "2026-10-31"]
    assert df["Close"].tolist() == [56000.0, 56300.0]
    get = s.calls[-1]
    assert get["headers"]["Authorization"] == "Bearer TKN"
    assert get["params"]["fromDate"] == "01/10/2026" and get["params"]["toDate"] == "31/10/2026"
    assert get["params"]["symbol"] == "VNM"


def test_daily_ohlc_pages_until_short_page():
    full = [ROW(f"{(date(2020, 1, 1) + timedelta(days=i)):%d/%m/%Y}", 100) for i in range(1000)]
    s = FakeSession([TOKEN_OK, ohlc_page(full), ohlc_page([ROW("01/01/2024", 100)])])
    df = SsiClient("id", "secret", session=s).daily_ohlc("VNM", date(2020, 1, 1), date(2024, 1, 1))
    assert len(df) == 1001
    assert [c["params"]["pageIndex"] for c in s.calls if c["method"] == "GET"] == [1, 2]


def test_empty_ohlc_is_no_data():
    s = FakeSession([TOKEN_OK, ohlc_page([])])
    with pytest.raises(NoMarketDataError):
        SsiClient("id", "secret", session=s).daily_ohlc("ZZZ", date(2026, 1, 1), date(2026, 2, 1))


def test_token_reused_and_refreshed_once_on_401():
    s = FakeSession([TOKEN_OK, ohlc_page([ROW("30/10/2026", 1)]), (401, {}), TOKEN_OK,
                     ohlc_page([ROW("30/10/2026", 1)])])
    c = SsiClient("id", "secret", session=s)
    c.daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    c.daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert sum(1 for x in s.calls if x["method"] == "POST") == 2


def test_errors_do_not_leak_secrets():
    for replies in ([(200, {"status": 401, "message": "Invalid consumer"})], [TOKEN_OK, (500, {})]):
        with pytest.raises(VendorError) as e:
            SsiClient("id", "S3CRET", session=FakeSession(replies)).daily_ohlc(
                "VNM", date(2026, 1, 1), date(2026, 2, 1))
        assert "S3CRET" not in str(e.value) and "TKN" not in str(e.value)


def test_from_env_requires_keys(monkeypatch):
    monkeypatch.delenv("SSI_CONSUMER_ID", raising=False)
    with pytest.raises(VendorNotConfiguredError):
        SsiClient.from_env()


def test_daily_index_and_securities():
    idx = (200, {"status": "Success",
                 "data": [{"IndexId": "VNINDEX", "IndexValue": "1699.62", "TradingDate": "03/11/2026"}]})

    def sec(rows):
        return (200, {"status": "Success", "data": rows})

    s = FakeSession([TOKEN_OK, idx,
                     sec([{"market": "HOSE", "symbol": "VNM", "StockName": "Vinamilk",
                           "StockEnName": "Vietnam Dairy"}]),
                     sec([]), sec([])])
    c = SsiClient("id", "secret", session=s)
    assert c.daily_index("VNINDEX", date(2026, 11, 1), date(2026, 11, 3)).iloc[-1] == 1699.62
    assert c.securities()["VNM"] == {"name": "Vietnam Dairy", "market": "HOSE"}
