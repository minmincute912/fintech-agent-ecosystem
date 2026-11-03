"""Minimal SSI FastConnect Data REST client (end-of-day prices, index values, listings).

Endpoints, auth and paging per guide.ssi.com.vn api-specs and SSI's python-fcdata
client, read 2026-11-03. Errors are TradingAgents' vendor error types so its router
turns them into "no data" / "unavailable" signals instead of invented values.
"""

from __future__ import annotations

import logging
import os
from datetime import date

import pandas as pd
import requests
from tradingagents.dataflows.errors import NoMarketDataError, VendorNotConfiguredError, VendorUnavailableError

logger = logging.getLogger(__name__)

BASE_URL = "https://fc-data.ssi.com.vn/"
_TOKEN = "api/v2/Market/AccessToken"
_DAILY_OHLC = "api/v2/Market/DailyOhlc"
_DAILY_INDEX = "api/v2/Market/DailyIndex"
_SECURITIES = "api/v2/Market/Securities"
_PAGE_SIZE = 1000
_MAX_PAGES = 10  # SSI accepts pageIndex 1..10
_PRICE_COLS = ["Open", "High", "Low", "Close", "Volume"]


def _ssi_date(d: date) -> str:
    return d.strftime("%d/%m/%Y")


class SsiClient:
    def __init__(self, consumer_id: str, consumer_secret: str, session=None, base_url: str = BASE_URL):
        self._id = consumer_id
        self._secret = consumer_secret
        self._session = session or requests
        self._base = base_url
        self._token: str | None = None
        self._securities: dict[str, dict] | None = None

    @classmethod
    def from_env(cls) -> SsiClient:
        cid, secret = os.environ.get("SSI_CONSUMER_ID"), os.environ.get("SSI_CONSUMER_SECRET")
        if not cid or not secret:
            raise VendorNotConfiguredError("SSI_CONSUMER_ID and SSI_CONSUMER_SECRET must be set in .env")
        return cls(cid, secret)

    def _access_token(self) -> str:
        if self._token is None:
            try:
                resp = self._session.post(self._base + _TOKEN, json={"consumerID": self._id,
                                                                      "consumerSecret": self._secret}, timeout=30)
                body = resp.json()
            except (requests.RequestException, ValueError) as e:
                raise VendorUnavailableError(f"SSI {_TOKEN} failed: {type(e).__name__}") from None
            if body.get("status") != 200:
                raise VendorNotConfiguredError(f"SSI token request failed: {body.get('message')}")
            self._token = body["data"]["accessToken"]
        return self._token

    def _get_once(self, path: str, params: dict):
        headers = {"Accept": "application/json", "Authorization": "Bearer " + self._access_token()}
        try:
            return self._session.get(self._base + path, params=params, headers=headers, timeout=30)
        except requests.RequestException as e:
            # from None: the chained exception can carry the request headers
            raise VendorUnavailableError(f"SSI {path} failed: {type(e).__name__}") from None

    def _get(self, path: str, params: dict) -> list[dict]:
        """All rows of a paged GET, refreshing the token once on HTTP 401."""
        rows: list[dict] = []
        for page in range(1, _MAX_PAGES + 1):
            query = {**params, "pageIndex": page, "pageSize": _PAGE_SIZE}
            resp = self._get_once(path, query)
            if resp.status_code == 401:
                self._token = None
                resp = self._get_once(path, query)
            if not 200 <= resp.status_code < 300:
                raise VendorUnavailableError(f"SSI {path} failed: HTTP {resp.status_code}")
            data = resp.json().get("data") or []
            rows.extend(data)
            if len(data) < _PAGE_SIZE:
                return rows
        # shortcut: 10k rows max per call (SSI paging cap), split the date range if a caller needs more
        logger.warning("SSI %s hit the %d-page cap; later rows were not fetched", path, _MAX_PAGES)
        return rows

    def daily_ohlc(self, symbol: str, start: date, end: date) -> pd.DataFrame:
        rows = self._get(_DAILY_OHLC, {"symbol": symbol, "fromDate": _ssi_date(start),
                                       "toDate": _ssi_date(end), "ascending": "true"})
        if not rows:
            raise NoMarketDataError(symbol, symbol, f"SSI DailyOhlc returned no rows {start}..{end}")
        df = pd.DataFrame(rows)
        out = pd.DataFrame({"Date": pd.to_datetime(df["TradingDate"], format="%d/%m/%Y")})
        for col in _PRICE_COLS:
            out[col] = pd.to_numeric(df[col], errors="coerce").astype(float)
        return out.drop_duplicates("Date", keep="last").sort_values("Date").reset_index(drop=True)

    def daily_index(self, index_id: str, start: date, end: date) -> pd.Series:
        rows = self._get(_DAILY_INDEX, {"indexId": index_id, "fromDate": _ssi_date(start),
                                        "toDate": _ssi_date(end), "ascending": "true"})
        if not rows:
            raise NoMarketDataError(index_id, index_id, f"SSI DailyIndex returned no rows {start}..{end}")
        df = pd.DataFrame(rows)
        values = pd.to_numeric(df["IndexValue"], errors="coerce").astype(float)
        values.index = pd.DatetimeIndex(pd.to_datetime(df["TradingDate"], format="%d/%m/%Y"), name="Date")
        return values[~values.index.duplicated(keep="last")].sort_index().rename(index_id)

    def securities(self) -> dict[str, dict]:
        if self._securities is None:
            listing = {}
            for market in ("HOSE", "HNX", "UPCOM"):
                for row in self._get(_SECURITIES, {"market": market}):
                    listing[row["symbol"]] = {"name": row.get("StockEnName") or row.get("StockName"),
                                              "market": row.get("market", market)}
            self._securities = listing
        return self._securities
