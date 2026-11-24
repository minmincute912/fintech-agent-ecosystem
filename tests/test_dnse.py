import base64
import hashlib
import hmac
import re
from datetime import date, datetime, timezone
from urllib import parse

import pytest
from tradingagents.dataflows.errors import (
    NoMarketDataError,
    VendorError,
    VendorNotConfiguredError,
    VendorUnavailableError,
)

from vsi.dnse import DnseClient


class _Resp:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class FakeSession:
    """Replies from a queue of (status_code, json) pairs and records every GET."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []

    def get(self, url, params=None, headers=None, timeout=None):
        self.calls.append({"url": url, "params": dict(params or {}), "headers": dict(headers)})
        return _Resp(*self.replies.pop(0))


def utc_midnight(d):
    return int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())


def bars(days, closes, next_time=0):
    return (200, {"t": [utc_midnight(d) for d in days], "o": closes, "h": [c + 0.1 for c in closes],
                  "l": [c - 0.1 for c in closes], "c": closes, "v": [1000] * len(closes), "nextTime": next_time})


def test_daily_ohlc_parses_sorts_and_queries_daily_stock_bars():
    s = FakeSession([bars([date(2026, 10, 31), date(2026, 10, 30)], [56.3, 56.0])])
    df = DnseClient("KEY", "secret", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert df["Date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-10-30", "2026-10-31"]
    assert df["Close"].tolist() == [56.0, 56.3]
    call = s.calls[-1]
    assert call["url"] == "https://openapi.dnse.com.vn/price/ohlc"
    p = call["params"]
    assert (p["symbol"], p["type"], p["resolution"]) == ("VNM", "STOCK", "1D")
    # whole Vietnam-time days: 2026-10-01 00:00 +07 .. 2026-10-31 23:59:59 +07
    assert (p["from"], p["to"]) == (1790787600, 1793465999)


def test_request_is_signed_like_the_dnse_sdk():
    s = FakeSession([bars([date(2026, 10, 30)], [56.0])])
    DnseClient("KEY", "S3CRET", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    h = s.calls[-1]["headers"]
    assert h["x-api-key"] == "KEY" and h["version"] == "2026-07-23"
    sig = dict(re.findall(r'(\w+)="([^"]*)"', h["X-Signature"]))
    assert sig["keyId"] == "KEY" and sig["algorithm"] == "hmac-sha256"
    assert sig["headers"] == "(request-target) date" and len(sig["nonce"]) == 32
    # signed string per developers.dnse.com.vn/docs/guide/intro/authentication: path only, no query
    signed = f"(request-target): get /price/ohlc\ndate: {h['Date']}\nnonce: {sig['nonce']}"
    expected = base64.b64encode(hmac.new(b"S3CRET", signed.encode(), hashlib.sha256).digest()).decode()
    assert sig["signature"] == parse.quote(expected, safe="")
    assert "S3CRET" not in str(h)


def test_vietnam_midnight_timestamps_keep_their_vietnam_date():
    vn_midnight_oct30 = 1793293200  # 2026-10-30 00:00 +07 = 2026-10-29 17:00 UTC
    s = FakeSession([(200, {"t": [vn_midnight_oct30], "o": [1], "h": [1], "l": [1], "c": [1], "v": [1],
                            "nextTime": 0})])
    df = DnseClient("k", "s", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert df["Date"].iloc[0].strftime("%Y-%m-%d") == "2026-10-30"


def test_daily_ohlc_follows_next_time():
    first, second = [date(2026, 10, 29)], [date(2026, 10, 30)]
    s = FakeSession([bars(first, [1.0], next_time=utc_midnight(second[0])), bars(second, [2.0])])
    df = DnseClient("k", "s", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert df["Close"].tolist() == [1.0, 2.0]
    assert s.calls[1]["params"]["from"] == utc_midnight(second[0])


def test_empty_ohlc_is_no_data():
    s = FakeSession([bars([], [])])
    with pytest.raises(NoMarketDataError):
        DnseClient("k", "s", session=s).daily_ohlc("ZZZ", date(2026, 1, 1), date(2026, 2, 1))


def test_http_error_is_unavailable_and_leaks_nothing():
    for reply in [(400, {"status": 400, "code": "OA-003", "message": "Thông tin nhập không hợp lệ"}),
                  (403, {"status": "error", "code": "OA-401", "message": "Quota exceeded"}),
                  (502, ValueError("not json"))]:
        with pytest.raises(VendorUnavailableError) as e:
            DnseClient("KEY", "S3CRET", session=FakeSession([reply])).daily_ohlc(
                "VNM", date(2026, 1, 1), date(2026, 2, 1))
        assert "S3CRET" not in str(e.value) and "KEY" not in str(e.value)


def test_network_error_keeps_no_context_with_secret():
    import requests

    class Boom(FakeSession):
        def get(self, url, params=None, headers=None, timeout=None):
            raise requests.ConnectionError(f"failed sending {headers}")

    with pytest.raises(VendorUnavailableError) as e:
        DnseClient("KEY", "S3CRET", session=Boom([])).daily_ohlc("VNM", date(2026, 1, 1), date(2026, 2, 1))
    assert e.value.__context__ is None and e.value.__cause__ is None
    assert isinstance(e.value, VendorError)


def test_from_env_requires_keys(monkeypatch):
    monkeypatch.delenv("DNSE_API_KEY", raising=False)
    with pytest.raises(VendorNotConfiguredError):
        DnseClient.from_env()


def test_daily_index_uses_index_bars():
    s = FakeSession([bars([date(2026, 11, 3)], [1699.62])])
    idx = DnseClient("k", "s", session=s).daily_index("VNINDEX", date(2026, 11, 1), date(2026, 11, 3))
    assert idx.iloc[-1] == 1699.62 and idx.name == "VNINDEX"
    assert idx.index[-1].strftime("%Y-%m-%d") == "2026-11-03"
    assert s.calls[-1]["params"]["type"] == "INDEX"


def test_instrument_maps_exchange_codes():
    row = {"symbol": "ACB", "marketId": "STO", "shortName": "Ngân hàng Á Châu", "name": "Ngân hàng TMCP Á Châu"}
    s = FakeSession([(200, {"data": [row]}), (200, {"data": []})])
    c = DnseClient("k", "s", session=s)
    assert c.instrument("ACB") == {"name": "Ngân hàng TMCP Á Châu", "market": "HOSE"}
    assert s.calls[0]["url"].endswith("/market/instruments") and s.calls[0]["params"] == {"symbol": "ACB"}
    assert c.instrument("ZZZ") is None
