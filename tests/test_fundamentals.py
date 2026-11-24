from datetime import date

import pandas as pd
import pytest
from tradingagents.dataflows.errors import NoMarketDataError

from vsi import fundamentals

RESTATED = "Values as currently held by the source; may include later restatements."


def _rows(fiscal, created, modified=None, items=None, model=2):
    items = items if items is not None else {21001: 100.0, 23000: 10.0}
    return [{"model_type": model, "fiscal_date": date.fromisoformat(fiscal), "item_code": code, "value": v,
             "created": date.fromisoformat(created), "modified": date.fromisoformat(modified or created)}
            for code, v in items.items()]


class FakeClient:
    def __init__(self, rows, layout=("corporate", (1, 2, 3))):
        self.df = pd.DataFrame(rows)
        self._layout = layout

    def statements(self, symbol, report_type):
        return self.df

    def layout_models(self, symbol):
        return self._layout

    def item_names(self, symbol, models):
        return {(2, 21001): ("Doanh thu thuần", "Net Sales", 140.0),
                (2, 23000): ("Lợi nhuận sau thuế của Công ty mẹ", "Net Profit After Tax of Parent Company", 660.0)}


@pytest.fixture
def client(monkeypatch):
    def use(rows, **kw):
        fake = FakeClient(rows, **kw)
        monkeypatch.setattr(fundamentals, "_client", fake)
        return fake
    return use


QUARTERS = [("2025-06-30", "2025-07-30"), ("2025-09-30", "2025-10-30"), ("2025-12-31", "2026-01-30"),
            ("2026-03-31", "2026-04-29"), ("2026-06-30", "2026-07-30"), ("2026-09-30", "2026-10-30")]


def _all_quarters():
    return [r for f, c in QUARTERS for r in _rows(f, c)]


def test_tables_exclude_periods_created_after_as_of(client):
    client(_all_quarters())
    out = fundamentals.get_income_statement("VNM.VN", "quarterly", "2026-10-29")
    assert "2026-06-30" in out and "2026-09-30" not in out


def test_tables_keep_latest_four(client):
    client(_all_quarters())
    out = fundamentals.get_income_statement("VNM.VN", "quarterly", "2026-11-25")
    for kept in ("2026-09-30", "2026-06-30", "2026-03-31", "2025-12-31"):
        assert kept in out
    assert "2025-09-30" not in out and "2025-06-30" not in out


def test_missing_item_is_blank(client):
    client(_rows("2026-09-30", "2026-10-30") + _rows("2026-06-30", "2026-07-30", items={21001: 90.0}))
    out = fundamentals.get_income_statement("VNM", "quarterly", "2026-11-25")
    row = next(line for line in out.splitlines() if "Net Profit After Tax of Parent Company" in line)
    assert row.rstrip().endswith("| 10 |  |")  # newest first; the missing Q2 cell is blank, not 0


def test_revised_period_marked(client):
    client(_rows("2026-09-30", "2026-10-30") + _rows("2026-06-30", "2026-07-30", modified="2026-08-17"))
    out = fundamentals.get_income_statement("VNM", "quarterly", "2026-08-01")
    assert "2026-06-30 (created 2026-07-30) (revised after analysis date)" in out
    assert "revised" not in fundamentals.get_income_statement("VNM", "quarterly", "2026-11-25").split("\n\n", 1)[1]


def test_header_lines(client):
    client(_all_quarters())
    out = fundamentals.get_income_statement("VNM", "quarterly", "2026-11-25")
    head = out.split("\n\n", 1)[0]
    assert RESTATED in head
    assert "VNDirect finfo" in head and "research-only, personal use" in head
    assert "created on or before 2026-11-25" in head and "layout: corporate" in head


def test_statement_picked_by_layout_position(client):
    rows = _rows("2026-09-30", "2026-10-30", items={12700: 500.0}, model=1) + _rows("2026-09-30", "2026-10-30")
    client(rows)
    assert "| 500 |" in fundamentals.get_balance_sheet("VNM", "quarterly", "2026-11-25")
    assert "| 500 |" not in fundamentals.get_income_statement("VNM", "quarterly", "2026-11-25")


def test_no_period_before_as_of_is_no_data(client):
    client(_all_quarters())
    with pytest.raises(NoMarketDataError):
        fundamentals.get_income_statement("VNM", "quarterly", "2025-07-29")
