import pandas as pd
import pytest
from tradingagents.dataflows.config import set_config
from tradingagents.dataflows.errors import NoMarketDataError, VendorUnavailableError

from vsi import bridge
from vsi.markets import vn_config

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

    def instrument(self, symbol):
        return {"name": "Vietnam Dairy", "market": "HOSE"} if symbol == "VNM" else None


class FakeFinfo:
    """One VNM income-statement row, created 2026-10-30."""

    def statements(self, symbol, report_type):
        from datetime import date
        return pd.DataFrame([{"model_type": 2, "fiscal_date": date(2026, 9, 30), "item_code": 21001,
                              "value": 18465190628493.0, "created": date(2026, 10, 30), "modified": date(2026, 10, 30)}])

    def layout_models(self, symbol):
        return "corporate", (1, 2, 3)

    def item_names(self, symbol, models):
        return {(2, 21001): ("Doanh thu thuần", "Net Sales", 140.0)}


@pytest.fixture
def installed(monkeypatch):
    cfg = vn_config()
    bridge.load_ohlcv.cache_clear()
    monkeypatch.setattr(bridge, "_client", None)  # records the original so teardown restores it
    bridge.install(FakeClient(), finfo=FakeFinfo(), patch=monkeypatch.setattr, setitem=monkeypatch.setitem)
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

    assert "Source: DNSE OpenAPI" in route_to_vendor("get_stock_data", "VNM.VN", "2026-10-01", "2026-10-30")
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


def test_stale_data_is_no_data(installed, monkeypatch):
    from tradingagents.dataflows.vendors.yahoo.snapshot import build_verified_market_snapshot

    class Stale(FakeClient):
        def daily_ohlc(self, symbol, start, end):
            df = super().daily_ohlc(symbol, start, end)
            return df[df["Date"] <= pd.Timestamp("2026-03-31")].reset_index(drop=True)

    monkeypatch.setattr(bridge, "_client", Stale())
    with pytest.raises(NoMarketDataError):
        bridge.load_ohlcv("VNM.VN", "2026-10-30")
    with pytest.raises(NoMarketDataError):
        build_verified_market_snapshot("VNM.VN", "2026-10-30", 5)


def test_news_routes_to_vsi(installed, tmp_path, monkeypatch):
    from datetime import datetime, timezone

    from tradingagents.dataflows.router import route_to_vendor

    from vsi import news
    store = news.NewsStore(tmp_path / "news.sqlite")
    store.add([news.NewsItem("Vietnam Dairy mở nhà máy mới", "", "https://example.vn/a", "CafeF",
                             datetime(2026, 11, 21, 3, tzinfo=timezone.utc))])
    monkeypatch.setattr(news, "_store", store)
    monkeypatch.setattr(news, "_refreshed", True)  # no live collect in tests
    out = route_to_vendor("get_news", "VNM.VN", "2026-11-20", "2026-11-23")
    assert "Vietnam Dairy mở nhà máy mới" in out  # matched by the DNSE company name, not the ticker
    assert "Vietnamese market" in route_to_vendor("get_global_news", "2026-11-23", 7, 10)


@pytest.mark.parametrize("method,args", [
    ("get_macro_indicators", ("cpi", "2026-11-23", 30)),
    ("get_prediction_markets", ("Fed rate cut", 5, "2026-11-23")),
    ("get_insider_transactions", ("VNM.VN", "2026-11-23")),
])
def test_us_only_tools_unavailable(installed, method, args):
    from tradingagents.dataflows.router import route_to_vendor
    out = route_to_vendor(method, *args)
    assert out.startswith("DATA_UNAVAILABLE") and "no Vietnamese source" in out


def test_fundamentals_routes_to_vsi(installed):
    from tradingagents.dataflows.router import route_to_vendor
    assert "18,465,190,628,493" in route_to_vendor("get_fundamentals", "VNM.VN", "2026-11-23")
    assert "Net Sales" in route_to_vendor("get_income_statement", "VNM.VN", "quarterly", "2026-11-23")
    assert route_to_vendor("get_balance_sheet", "VNM.VN", "quarterly", "2026-10-29").startswith("NO_DATA_AVAILABLE")
