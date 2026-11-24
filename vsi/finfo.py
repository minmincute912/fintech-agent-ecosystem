"""VNDirect finfo financial statements (undocumented public API; research-only, personal use).

Owner decision 2026-11-24 (M2 design, option A). No key; terms page unreadable (403). Shapes seen
in the 2026-11-24 probe: statements rows {itemCode, modelType, numericValue, fiscalDate,
createdDate, modifiedDate}; models rows add {itemVnName, itemEnName, displayOrder}. Errors are
TradingAgents' vendor error types, so a broken source reads as DATA_UNAVAILABLE, never as numbers.
"""

from __future__ import annotations

from typing import Literal

import pandas as pd
import requests
from tradingagents.dataflows.errors import NoMarketDataError, VendorUnavailableError

BASE_URL = "https://api-finfo.vndirect.com.vn/v4/"
# balance-sheet model type -> (layout, (balance sheet, income statement, cash flow) model types)
LAYOUTS = {
    1: ("corporate", (1, 2, 3)),
    101: ("bank", (101, 102, 103)),
    89: ("securities", (89, 90, 91)),
    411: ("insurance", (411, 412, 413)),
}
_ROWS = 10000  # newest first; about 50 quarters of one company's items


class FinfoClient:
    def __init__(self, session=None):
        self._session = session or requests
        self._cache: dict[tuple[str, str], pd.DataFrame] = {}

    def _get(self, endpoint: str, params: dict) -> list[dict]:
        failure = None
        try:
            resp = self._session.get(BASE_URL + endpoint, params=params, timeout=30)
        except requests.RequestException as e:
            failure = type(e).__name__
        if failure:  # raised outside the except: no chained traceback in tool output
            raise VendorUnavailableError(f"finfo {endpoint} failed: {failure}")
        try:
            body = resp.json()
        except ValueError:
            body = None
        if not 200 <= resp.status_code < 300 or not isinstance(body, dict) or not isinstance(body.get("data"), list):
            raise VendorUnavailableError(f"finfo {endpoint} failed: HTTP {resp.status_code} or unexpected body")
        return body["data"]

    def statements(self, symbol: str, report_type: Literal["QUARTER", "ANNUAL"]) -> pd.DataFrame:
        symbol = symbol.strip().upper()
        key = (symbol, report_type)
        if key not in self._cache:
            rows = self._get("financial_statements", {"q": f"code:{symbol}~reportType:{report_type}",
                                                      "sort": "fiscalDate:desc", "size": _ROWS})
            if not rows:
                raise NoMarketDataError(symbol, symbol, f"finfo has no {report_type.lower()} statements")
            raw = pd.DataFrame(rows)
            day = lambda col: pd.to_datetime(raw[col]).dt.date  # noqa: E731
            self._cache[key] = pd.DataFrame({
                "model_type": raw["modelType"].astype(int), "fiscal_date": day("fiscalDate"),
                "item_code": raw["itemCode"].astype(int), "value": raw["numericValue"].astype(float),
                "created": day("createdDate"), "modified": day("modifiedDate"),
            })
        return self._cache[key]

    def layout(self, symbol: str) -> str:
        return self.layout_models(symbol)[0]

    def layout_models(self, symbol: str) -> tuple[str, tuple[int, int, int]]:
        present = set(self.statements(symbol, "QUARTER")["model_type"])
        for name, models in LAYOUTS.values():
            if present & set(models):
                return name, models
        raise NoMarketDataError(symbol, symbol, f"finfo layout {sorted(present)} not supported")

    def item_names(self, symbol: str, model_types: list[int]) -> dict[tuple[int, int], tuple[str, str, float]]:
        """(model type, item code) -> (Vietnamese name, English name, display order)."""
        types = ",".join(str(m) for m in model_types)
        rows = self._get("financial_models", {"q": f"codeList:{symbol.strip().upper()}~modelType:{types}", "size": 999})
        return {(int(r["modelType"]), int(r["itemCode"])): (r.get("itemVnName") or "", r.get("itemEnName") or "",
                                                             float(r.get("displayOrder") or 0)) for r in rows}
