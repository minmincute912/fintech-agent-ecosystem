"""Feed DNSE OpenAPI market data into TradingAgents v0.7.1 and keep Yahoo out.

TradingAgents routes get_stock_data/get_indicators through its vendor router, but
loads prices for indicators, the verified snapshot and settlement, and company
identity, by calling Yahoo helpers directly. install() points those names at DNSE
so the upstream indicator, snapshot and settlement code runs unchanged on DNSE data,
and disables yfinance so any path left over fails loudly instead of fetching. Vietnamese
news (vsi.news) and "no Vietnamese source" stubs for US-only tools register as vendor "vsi".
"""

from __future__ import annotations

import functools
import operator
from datetime import timedelta

import pandas as pd
import yfinance
from tradingagents.agents import context
from tradingagents.dataflows import router
from tradingagents.dataflows.errors import NoMarketDataError, VendorUnavailableError
from tradingagents.dataflows.vendors.yahoo import market, snapshot
from tradingagents.dataflows.vendors.yahoo.ohlcv import _assert_ohlcv_not_stale
from tradingagents.memory import settlement

from vsi import news
from vsi.dnse import DnseClient

INDEX_CODES = frozenset({"VNINDEX"})
_VN_TZ = "Asia/Ho_Chi_Minh"
_client: DnseClient | None = None


def base_symbol(symbol: str) -> str:
    sym = symbol.strip().upper()
    return sym[:-3] if sym.endswith(".VN") else sym


def _day(value: str):
    return pd.Timestamp(value).date()


@functools.lru_cache(maxsize=64)
def _ohlcv_until(base: str, as_of_date: str) -> pd.DataFrame:
    as_of = _day(as_of_date)
    df = _client.daily_ohlc(base, as_of - timedelta(days=5 * 365), as_of)
    df = df[df["Date"] <= pd.Timestamp(as_of)].dropna(subset=["Close"])
    if df.empty:
        raise NoMarketDataError(base, base, f"no DNSE price rows on or before {as_of_date}")
    _assert_ohlcv_not_stale(df, as_of_date, base, base)  # upstream guard: halted/delisted is not "latest"
    return df.reset_index(drop=True)


def load_ohlcv(symbol: str, as_of_date: str, fill_gaps: bool = True) -> pd.DataFrame:
    """Same contract as TradingAgents' Yahoo load_ohlcv: rows up to as_of_date only."""
    # shortcut: fill_gaps ignored — DNSE returns traded sessions only; revisit if a halted stock shows gaps
    return _ohlcv_until(base_symbol(symbol), str(as_of_date)[:10]).copy()  # callers mutate the frame


load_ohlcv.cache_clear = _ohlcv_until.cache_clear


def get_stock_data(symbol: str, start_date: str, end_date: str) -> str:
    base = base_symbol(symbol)
    df = _client.daily_ohlc(base, _day(start_date), _day(end_date))
    df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))]
    if df.empty:
        raise NoMarketDataError(symbol, base, f"no DNSE rows between {start_date} and {end_date}")
    out = df.assign(Date=df["Date"].dt.strftime("%Y-%m-%d"))
    header = (f"# Stock data for {base} from {start_date} to {end_date}\n"
              f"# Total records: {len(out)}\n# Source: DNSE OpenAPI; prices in thousand VND\n\n")
    return header + out.to_csv(index=False)


def get_closes(symbol: str, start_date: str, end_date: str) -> pd.Series:
    """Daily closes from start_date up to, not including, end_date (Yahoo get_closes contract)."""
    base = base_symbol(symbol)
    start, last = _day(start_date), _day(end_date) - timedelta(days=1)
    if base in INDEX_CODES:
        closes = _client.daily_index(base, start, last)
    else:
        df = _client.daily_ohlc(base, start, last)
        closes = pd.Series(df["Close"].to_numpy(), index=pd.DatetimeIndex(df["Date"], name="Date"))
    closes = closes[(closes.index >= pd.Timestamp(start)) & (closes.index <= pd.Timestamp(last))]
    # Vietnam time zone so settlement treats a still-trading VN session as today, not UTC's day
    return closes.tz_localize(_VN_TZ).rename("Close")


def company_profile(ticker: str) -> dict:
    info = _client.instrument(base_symbol(ticker))
    return {"longName": info["name"], "exchange": info["market"]} if info else {}


def _names_for(symbol: str) -> list[str]:
    info = _client.instrument(symbol)
    return [info["name"]] if info and info.get("name") else []


def _no_vn_source(method: str):
    def unavailable(*args, **kwargs):
        raise VendorUnavailableError(f"no Vietnamese source for {method}; do not use US data for a Vietnamese stock")
    return unavailable


VSI_METHODS = {
    "get_news": news.get_news,
    "get_global_news": news.get_global_news,
    **{m: _no_vn_source(m) for m in ("get_insider_transactions", "get_macro_indicators", "get_prediction_markets")},
}


def _yahoo_blocked(*args, **kwargs):
    raise VendorUnavailableError(
        "Yahoo disabled: its terms forbid automated access (docs/research/yahoo-vn-probe.md)")


# shortcut: patches TradingAgents v0.7.1 internals by name; test_bridge fails loudly if an upgrade
# renames them — re-check on every version bump.
def install(client: DnseClient, patch=setattr, setitem=operator.setitem) -> None:
    global _client
    _client = client
    setitem(router.VENDOR_METHODS["get_stock_data"], "dnse", get_stock_data)
    setitem(router.VENDOR_METHODS["get_indicators"], "dnse", market.get_stock_stats_indicators_window)
    for method, func in VSI_METHODS.items():
        if method not in router.VENDOR_METHODS:
            raise RuntimeError(f"TradingAgents changed: router has no {method}; re-check vsi.bridge")
        setitem(router.VENDOR_METHODS[method], "vsi", func)
    for module, name, value in (
        (market, "load_ohlcv", load_ohlcv),
        (snapshot, "load_ohlcv", load_ohlcv),
        (market, "get_closes", get_closes),
        (settlement, "get_closes", get_closes),
        (context, "get_company_profile", company_profile),
        (news, "names_for", _names_for),
        (yfinance, "Ticker", _yahoo_blocked),
        (yfinance, "download", _yahoo_blocked),
        (yfinance, "Search", _yahoo_blocked),
    ):
        if not hasattr(module, name):
            raise RuntimeError(f"TradingAgents changed: {module.__name__}.{name} is gone; re-check vsi.bridge")
        patch(module, name, value)
    context._identity.cache_clear()
