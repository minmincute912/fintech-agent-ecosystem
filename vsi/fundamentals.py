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


_PER_SHARE = {23001, 700087}  # EPS, diluted EPS: VND per share, not amounts


def _cell(value, code: int | None = None) -> str:
    """Billion VND, 2 decimals: the agent quotes these as-is instead of converting raw VND (it slipped 1000x)."""
    if pd.isna(value):
        return ""
    return f"{value:,.0f} (VND per share)" if code in _PER_SHARE else f"{value / 1e9:,.2f}"


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
            "# Source: VNDirect finfo (undocumented public API), research-only, personal use. Values in billion VND (tỷ đồng) unless marked.",
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
        lines.append(f"| {vn} | {en} | " + " | ".join(_cell(v, code) for v in row) + " |")
    return "\n".join(head) + "\n\n" + "\n".join(lines)


def get_balance_sheet(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 0)


def get_income_statement(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 1)


def get_cashflow(ticker: str, freq: str = "quarterly", as_of_date: str | None = None) -> str:
    return _table(ticker, freq, as_of_date, 2)


# --- code-computed summary (get_fundamentals). Item codes from finfo-items.txt (probe 2026-11-25). ---

_NPAT, _PARENT = "Net profit after tax", "Net profit, parent shareholders"
SUMMARY_ITEMS: dict[str, dict[str, tuple[int, int]]] = {
    "corporate": {"Revenue": (2, 21001), "Gross profit": (2, 23100), _NPAT: (2, 23003), _PARENT: (2, 23000),
                  "Operating cash flow": (3, 32000), "Total assets": (1, 12700), "Equity": (1, 14000)},
    "bank": {"Net interest income": (102, 421900), "Total operating income": (102, 421701),
             "Operating expenses": (102, 22200), "Credit-loss provisions": (102, 422900), _NPAT: (102, 23003),
             _PARENT: (102, 23000), "Total assets": (101, 12700), "Customer loans": (101, 412100),
             "Customer deposits": (101, 413300), "Equity": (101, 14000)},
    "securities": {"Operating revenue": (90, 21001), "Gains on FVTPL financial assets": (90, 700039),
                   "Income from loans and receivables": (90, 700044), "Brokerage revenue": (90, 621110),
                   _NPAT: (90, 23003), _PARENT: (90, 23000), "Total assets": (89, 12700),
                   "Margin and other loans": (89, 700001), "Equity": (89, 14000)},
    "insurance": {"Net premium revenue": (412, 21440), "Gross written premium": (412, 21410), _NPAT: (412, 23003),
                  _PARENT: (412, 23000), "Total assets": (411, 12700), "Equity": (411, 14000)},
}
# label -> (minuend, subtrahend), both from SUMMARY_ITEMS of the same layout
_DERIVED = {"bank": {"Non-interest income (computed)": ("Total operating income", "Net interest income")}}


def _pct(value, base) -> str:
    if pd.isna(value) or pd.isna(base) or base <= 0:
        return ""
    return f"{(value - base) / base * 100:+.1f}"


def get_fundamentals(ticker: str, as_of_date: str | None = None) -> str:
    symbol, as_of = _symbol(ticker), _as_of(as_of_date)
    layout, _ = _client.layout_models(symbol)
    df = _usable(symbol, "QUARTER", as_of)
    latest = max(df["fiscal_date"])
    prev = (pd.Timestamp(latest) - pd.offsets.QuarterEnd(1)).date()
    year_ago = (pd.Timestamp(latest) - pd.DateOffset(years=1)).date()
    by_key = df.groupby(["model_type", "item_code", "fiscal_date"])["value"].last()

    def value(key, period):
        return by_key.get((*key, period), float("nan"))

    rows, missing = {}, []
    for label, key in SUMMARY_ITEMS[layout].items():
        if not any(k[:2] == key for k in by_key.index):
            missing.append(label)
            continue
        rows[label] = [value(key, p) for p in (latest, prev, year_ago)]
    for label, (a, b) in _DERIVED.get(layout, {}).items():
        if a in rows and b in rows:
            derived = [x - y for x, y in zip(rows[a], rows[b])]
            items = list(rows.items())
            at = [k for k, _ in items].index(a) + 1  # shown right after the line it is computed from
            rows = dict(items[:at] + [(label, derived)] + items[at:])
    created = df[df["fiscal_date"] == latest]["created"].min()
    revised = df[df["fiscal_date"] == latest]["modified"].max() > as_of
    head = [f"# Fundamentals summary for {symbol}, layout: {layout}, quarterly, as of {as_of}",
            "# Source: VNDirect finfo (undocumented public API), research-only, personal use. Values in billion VND (tỷ đồng) unless marked.",
            f"# {RESTATED}",
            "# QoQ: change vs previous quarter; YoY: vs same quarter a year earlier; % computed by code, "
            "blank when a value is missing or the base is not positive. Quarterly figures are for the quarter alone.",
            f"Latest usable quarter: {latest} (created {created})" + (" (revised after analysis date)" if revised else "")]
    lines = [f"| Item | {latest} | QoQ % | YoY % | {prev} | {year_ago} |", "|---|---|---|---|---|---|"]
    for label, (cur, before, last_year) in rows.items():
        lines.append(f"| {label} | {_cell(cur)} | {_pct(cur, before)} | {_pct(cur, last_year)} | "
                     f"{_cell(before)} | {_cell(last_year)} |")
    tail = [f"Not in source data: {', '.join(missing)}"] if missing else []
    return "\n".join(head) + "\n\n" + "\n".join(lines + tail)
