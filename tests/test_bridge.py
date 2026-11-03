import copy

import pandas as pd
import pytest
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.errors import NoMarketDataError, VendorUnavailableError
from tradingagents.default_config import DEFAULT_CONFIG

from vsi import bridge

DATES = pd.bdate_range(end="2026-10-30", periods=300)


class FakeClient:
    """300 business days ending 2026-10-30; close = 50000 + 10*i, VNINDEX = 1600 + i."""

    def daily_ohlc(self, symbol, start, end):
        if symbol != "VNM":
            raise NoMarketDataError(symbol, symbol, "fake: unknown")
        close = pd.Series([50000.0 + 10 * i for i in range(len(DATES))])
        df = pd.DataFrame({"Date": DATES, "Open": close, "High": close + 100, "Low": close - 100,
                           "Close": close, "Volume": 1000.0})
        return df[(df["Date"] >= pd.Timestamp(start)) & (df["Date"] <= pd.Timestamp(end))].reset_index(drop=True)

    def daily_index(self, index_id, start, end):
        s = pd.Series([1600.0 + i for i in range(len(DATES))], index=pd.DatetimeIndex(DATES, name="Date"))
        return s[(s.index >= pd.Timestamp(start)) & (s.index <= pd.Timestamp(end))]

    def securities(self):
        return {"VNM": {"name": "Vietnam Dairy", "market": "HOSE"}}


@pytest.fixture
def installed(monkeypatch):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["data_vendors"].update(core_stock_apis="ssi", technical_indicators="ssi")
    bridge.load_ohlcv.cache_clear()
    bridge.install(FakeClient(), patch=monkeypatch.setattr, setitem=monkeypatch.setitem)
    monkeypatch.setattr(bridge, "_client", bridge._client)  # undo the module global after the test
    set_config(cfg)
    yield
    bridge.load_ohlcv.cache_clear()


def test_load_ohlcv_cuts_at_as_of(installed):
    df = bridge.load_ohlcv("VNM.VN", "2026-06-30")
    assert df["Date"].max() <= pd.Timestamp("2026-06-30")
    assert list(df.columns[:6]) == ["Date", "Open", "High", "Low", "Close", "Volume"]


def test_market_tools_use_ssi(installed):
    from tradingagents.agents.context import resolve_instrument_identity
    from tradingagents.dataflows.router import route_to_vendor
    from tradingagents.dataflows.vendors.yahoo.snapshot import build_verified_market_snapshot
    from tradingagents.memory import settlement

    assert "Source: SSI FastConnect Data" in route_to_vendor("get_stock_data", "VNM.VN", "2026-10-01", "2026-10-30")
    assert "rsi" in route_to_vendor("get_indicators", "VNM.VN", "rsi", "2026-10-30", 10).lower()
    assert "52990" in build_verified_market_snapshot("VNM.VN", "2026-10-30", 5)  # last close 50000+10*299
    assert settlement.get_closes("VNINDEX", "2026-10-01", "2026-10-31").iloc[-1] == 1600 + 299
    assert resolve_instrument_identity("VNM.VN")["company_name"] == "Vietnam Dairy"


def test_unknown_ticker_is_no_data(installed):
    from tradingagents.dataflows.router import route_to_vendor
    assert route_to_vendor("get_stock_data", "ZZZ.VN", "2026-10-01", "2026-10-30").startswith("NO_DATA_AVAILABLE")


def test_yahoo_is_blocked(installed):
    import yfinance
    with pytest.raises(VendorUnavailableError):
        yfinance.Ticker("VNM.VN")


def test_get_closes_end_exclusive(installed):
    s = bridge.get_closes("VNM.VN", "2026-10-28", "2026-10-30")
    assert s.index.max() < pd.Timestamp("2026-10-30", tz="Asia/Ho_Chi_Minh")
    assert s.index.max() == pd.Timestamp("2026-10-29", tz="Asia/Ho_Chi_Minh")
