"""Fundamentals tools on VNDirect finfo statements, cut at the analysis date.

A period is usable on date D only if finfo's createdDate <= D (finfo-probe.md: createdDate
sits on or a day after first publication). finfo keeps current values only, so periods
revised after D are labelled. Every number is the source value; nothing is estimated.
"""

from __future__ import annotations

from datetime import date

import pandas as pd
from tradingagents.dataflows.errors import NoMarketDataError

from vsi.finfo import FinfoClient

RESTATED = "Values as currently held by the source; may include later restatements."
_REPORT = {"quarterly": "QUARTER", "annual": "ANNUAL"}
_STATEMENTS = ("Balance sheet", "Income statement", "Cash flow statement")
_PERIODS = 4
_client: FinfoClient | None = None


def _symbol(ticker: str) -> str:
    return ticker.strip().upper().removesuffix(".VN")


def _as_of(as_of_date: str | None) -> date:
    return date.fromisoformat(as_of_date[:10]) if as_of_date else date.today()


def _usable(symbol: str, report_type: str, as_of: date) -> pd.DataFrame:
    df = _client.statements(symbol, report_type)
    df = df[df["created"] <= as_of]
    if df.empty:
        raise NoMarketDataError(symbol, symbol, f"no finfo {report_type.lower()} statement created on or before {as_of}")
    return df


def _period_label(rows: pd.DataFrame, fiscal: date, as_of: date) -> str:
    label = f"{fiscal} (created {rows['created'].min()})"
    return label + " (revised after analysis date)" if rows["modified"].max() > as_of else label


def _cell(value) -> str:
    return "" if pd.isna(value) else f"{value:,.0f}"


def _table(ticker: str, freq: str, as_of_date: str | None, position: int) -> str:
    symbol, as_of = _symbol(ticker), _as_of(as_of_date)
    report_type = _REPORT.get(freq, "QUARTER")
    layout, models = _client.layout_models(symbol)
    model = models[position]
    df = _usable(symbol, report_type, as_of)
    df = df[df["model_type"] == model]
    periods = sorted(df["fiscal_date"].unique(), reverse=True)[:_PERIODS]
    if not periods:
        raise NoMarketDataError(symbol, symbol, f"no {_STATEMENTS[position].lower()} created on or before {as_of}")
    df = df[df["fiscal_date"].isin(periods)]
    values = df.pivot_table(index="item_code", columns="fiscal_date", values="value", aggfunc="last")
    values = values.reindex(columns=periods)
    names = _client.item_names(symbol, list(models))
    order = sorted(values.index, key=lambda code: (names.get((model, code), ("", "", float("inf")))[2], code))
    head = [f"# {_STATEMENTS[position]} for {symbol} ({freq}), layout: {layout}",
            "# Source: VNDirect finfo (undocumented public API), research-only, personal use. Values in VND.",
            f"# Periods shown: latest {_PERIODS} with a statement created on or before {as_of} "
            "(creation date approximates publication; see column headers).",
            f"# {RESTATED}"]
    lines = ["| Item (VI) | Item (EN) | " + " | ".join(_period_label(df[df["fiscal_date"] == p], p, as_of) for p in periods) + " |",
             "|---|---|" + "---|" * len(periods)]
    for code in order:
        row = values.loc[code]
        if all(pd.isna(v) or v == 0 for v in row):
            continue  # all-zero lines of the standard template carry no information
        vn, en, _ = names.get((model, code), (f"item {code}", f"item {code}", 0))
        lines.append(f"| {vn} | {en} | " + " | ".join(_cell(v) for v in row) + " |")
    return "\n".join(head) + "\n\n" + "\n".join(lines)


def get_balance_sheet(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 0)


def get_income_statement(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 1)


def get_cashflow(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 2)
