"""Minimal DNSE OpenAPI market-data client (daily bars, index bars, instrument identity).

Endpoints, signing and parameters per developers.dnse.com.vn (authentication, rate-limit
and OHLC pages) and the spec + Python SDK in github.com/dnse-tech/openapi-sdk, read
2026-11-24. Errors are TradingAgents' vendor error types so its router turns them into
"no data" / "unavailable" signals instead of invented values.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
import uuid
from datetime import date, datetime, time, timezone
from urllib import parse
from zoneinfo import ZoneInfo

import pandas as pd
import requests
from tradingagents.dataflows.errors import NoMarketDataError, VendorNotConfiguredError, VendorUnavailableError

logger = logging.getLogger(__name__)

BASE_URL = "https://openapi.dnse.com.vn"
API_VERSION = "2026-07-23"
_OHLC = "/price/ohlc"
_INSTRUMENTS = "/market/instruments"
_DATE_HEADER = "Date"  # SDK default; the spec YAML names X-Aux-Date instead (Task 8 probe confirms)
_MAX_PAGES = 50
_VN = ZoneInfo("Asia/Ho_Chi_Minh")
_EXCHANGES = {"STO": "HOSE", "STX": "HNX", "UPX": "UPCOM"}


class DnseClient:
    def __init__(self, api_key: str, api_secret: str, session=None, base_url: str = BASE_URL):
        self._key = api_key
        self._secret = api_secret
        self._session = session or requests
        self._base = base_url

    @classmethod
    def from_env(cls) -> DnseClient:
        key, secret = os.environ.get("DNSE_API_KEY"), os.environ.get("DNSE_API_SECRET")
        if not key or not secret:
            raise VendorNotConfiguredError("DNSE_API_KEY and DNSE_API_SECRET must be set in .env")
        return cls(key, secret)

    def _headers(self, path: str) -> dict:
        """HMAC-SHA256 over method + path (no query) + date + nonce, as dnse.api.common.build_signature."""
        stamp = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        nonce = uuid.uuid4().hex
        signed = f"(request-target): get {path}\n{_DATE_HEADER.lower()}: {stamp}\nnonce: {nonce}"
        digest = hmac.new(self._secret.encode(), signed.encode(), hashlib.sha256).digest()
        signature = parse.quote(base64.b64encode(digest).decode(), safe="")
        return {
            _DATE_HEADER: stamp,
            "X-Signature": (f'Signature keyId="{self._key}",algorithm="hmac-sha256",'
                            f'headers="(request-target) {_DATE_HEADER.lower()}",signature="{signature}",'
                            f'nonce="{nonce}"'),
            "x-api-key": self._key,
            "version": API_VERSION,
            "Accept": "application/json",
        }

    def _get(self, path: str, params: dict) -> dict:
        failure = None
        try:
            resp = self._session.get(self._base + path, params=params, headers=self._headers(path), timeout=30)
        except requests.RequestException as e:
            failure = type(e).__name__
        if failure:  # raised outside the except so no __context__ carries the request headers (key)
            raise VendorUnavailableError(f"DNSE {path} failed: {failure}")
        try:
            body = resp.json()
        except ValueError:
            body = None
        if not 200 <= resp.status_code < 300 or not isinstance(body, dict):
            detail = f"{body.get('code')} {body.get('message')}" if isinstance(body, dict) else "non-JSON response"
            raise VendorUnavailableError(f"DNSE {path} failed: HTTP {resp.status_code} {detail}")
        return body

    def daily_ohlc(self, symbol: str, start: date, end: date, kind: str = "STOCK") -> pd.DataFrame:
        """Daily bars dated in Vietnam time; prices in DNSE's unit (thousand VND for stocks)."""
        start_ts = int(datetime.combine(start, time.min, _VN).timestamp())
        end_ts = int(datetime.combine(end, time(23, 59, 59), _VN).timestamp())
        cols = {"t": [], "o": [], "h": [], "l": [], "c": [], "v": []}
        for _ in range(_MAX_PAGES):
            body = self._get(_OHLC, {"symbol": symbol, "type": kind, "resolution": "1D",
                                     "from": start_ts, "to": end_ts})
            for k in cols:
                cols[k].extend(body.get(k) or [])
            nxt = body.get("nextTime") or 0  # 0 = no more data
            if not start_ts < nxt <= end_ts:
                break
            start_ts = nxt
        else:
            # shortcut: page cap guards a server that never returns nextTime=0; narrow the range if hit
            logger.warning("DNSE %s hit the %d-page cap for %s", _OHLC, _MAX_PAGES, symbol)
        if not cols["t"]:
            raise NoMarketDataError(symbol, symbol, f"DNSE OHLC returned no daily bars {start}..{end}")
        days = pd.to_datetime(cols["t"], unit="s", utc=True).tz_convert(_VN).normalize().tz_localize(None)
        out = pd.DataFrame({"Date": days})
        for col, key in (("Open", "o"), ("High", "h"), ("Low", "l"), ("Close", "c"), ("Volume", "v")):
            out[col] = pd.to_numeric(pd.Series(cols[key]), errors="coerce").astype(float)
        return out.drop_duplicates("Date", keep="last").sort_values("Date").reset_index(drop=True)

    def daily_index(self, index_id: str, start: date, end: date) -> pd.Series:
        df = self.daily_ohlc(index_id, start, end, kind="INDEX")
        return pd.Series(df["Close"].to_numpy(), index=pd.DatetimeIndex(df["Date"], name="Date"), name=index_id)

    def instrument(self, symbol: str) -> dict | None:
        """{"name", "market"} for one listed symbol, or None when DNSE does not list it."""
        for row in self._get(_INSTRUMENTS, {"symbol": symbol}).get("data") or []:
            if row.get("symbol") == symbol:
                return {"name": row.get("name") or row.get("shortName"),
                        "market": _EXCHANGES.get(row.get("marketId"), row.get("marketId"))}
        return None
