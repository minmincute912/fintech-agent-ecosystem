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
    assert row.rstrip().endswith("| 0.00 |  |")  # 10 VND in billions; the missing Q2 cell is blank, not 0


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
    rows = _rows("2026-09-30", "2026-10-30", items={12700: 500e9}, model=1) + _rows("2026-09-30", "2026-10-30")
    client(rows)
    assert "| 500.00 |" in fundamentals.get_balance_sheet("VNM", "quarterly", "2026-11-25")
    assert "| 500.00 |" not in fundamentals.get_income_statement("VNM", "quarterly", "2026-11-25")


def test_no_period_before_as_of_is_no_data(client):
    client(_all_quarters())
    with pytest.raises(NoMarketDataError):
        fundamentals.get_income_statement("VNM", "quarterly", "2025-07-29")


# --- summaries (Task 8). Fixtures: live finfo rows for the summary items, fetched 2026-11-25. ---

import json  # noqa: E402
from pathlib import Path  # noqa: E402


class FixtureClient:
    def __init__(self, layout):
        data = json.loads((Path(__file__).parent / "fixtures" / f"finfo_{layout}.json").read_text())
        self.df = pd.DataFrame(data["rows"])
        for col in ("fiscal_date", "created", "modified"):
            self.df[col] = self.df[col].map(date.fromisoformat)
        self.names = {(m, i): (vn, en, order) for m, i, vn, en, order in data["names"]}
        self.models = tuple(sorted({m for m, _ in self.names}))
        self.layout = layout

    def statements(self, symbol, report_type):
        return self.df

    def layout_models(self, symbol):
        return self.layout, self.models

    def item_names(self, symbol, models):
        return self.names


def _summary(monkeypatch, layout, as_of="2026-11-25"):
    monkeypatch.setattr(fundamentals, "_client", FixtureClient(layout))
    return fundamentals.get_fundamentals("X.VN", as_of)


def _line(out, label):
    return next(line for line in out.splitlines() if line.startswith(f"| {label} "))


def _cells(out, label):
    return [c.strip() for c in _line(out, label).strip("|").split("|")]


def _bn(cell):  # "18,465.19" (billion VND) -> float
    return float(cell.replace(",", ""))


def test_summary_corporate_values_and_changes(monkeypatch):
    out = _summary(monkeypatch, "corporate")
    assert "Latest usable quarter: 2026-09-30 (created 2026-10-30)" in out
    label, value, qoq, yoy, prev, year_ago = _cells(out, "Revenue")
    assert value == "18,465.19" and prev == "18,847.35" and year_ago == "16,953.23"  # billion VND
    assert (qoq, yoy) == ("-2.0", "+8.9")  # (18465.19-18847.35)/18847.35, (18465.19-16953.23)/16953.23
    assert _cells(out, "Equity")[2] == "+7.3"


def test_summary_uses_only_statements_created_by_as_of(monkeypatch):
    out = _summary(monkeypatch, "corporate", "2026-10-29")
    assert "Latest usable quarter: 2026-06-30" in out


def test_summary_change_blank_when_base_not_positive(monkeypatch):
    fake = FixtureClient("corporate")
    q2 = (fake.df["fiscal_date"] == date(2026, 6, 30)) & (fake.df["item_code"] == 21001)
    fake.df.loc[q2, "value"] = 0.0
    monkeypatch.setattr(fundamentals, "_client", fake)
    assert _cells(fundamentals.get_fundamentals("VNM", "2026-11-25"), "Revenue")[2] == ""


def test_summary_bank_uses_net_interest_income(monkeypatch):
    out = _summary(monkeypatch, "bank")
    assert "| Revenue " not in out
    assert _cells(out, "Net interest income")[1] == "8,195.35"
    nii, total = _bn(_cells(out, "Net interest income")[1]), _bn(_cells(out, "Total operating income")[1])
    assert _bn(_cells(out, "Non-interest income (computed)")[1]) == pytest.approx(total - nii)


def test_summary_corporate_matches_published_vnm_q3_2026(monkeypatch):
    # Vinamilk Q3 2026 consolidated statement as reported by doanhnhan.baophapluat.vn (2026-10-31)
    # and diendandoanhnghiep.vn: net sales 18.465 tỷ, NPAT 2.962 tỷ, parent NPAT 2.964 tỷ.
    out = _summary(monkeypatch, "corporate")
    assert round(_bn(_cells(out, "Revenue")[1])) == 18465
    assert round(_bn(_cells(out, "Net profit after tax")[1])) == 2962
    assert round(_bn(_cells(out, "Net profit, parent shareholders")[1])) == 2964


def test_summary_bank_matches_published_acb_q3_2026(monkeypatch):
    # ACB Q3 2026 consolidated statement as reported by mekongasean.vn and cafef.vn (2026-10-28):
    # NPAT 4.698,8 tỷ; credit-loss provisions 933,8 tỷ; total assets above 1,1 triệu tỷ.
    out = _summary(monkeypatch, "bank")
    assert round(_bn(_cells(out, "Net profit after tax")[1]), 1) == 4698.8
    assert round(_bn(_cells(out, "Credit-loss provisions")[1]), 1) == 933.8
    assert _bn(_cells(out, "Total assets")[1]) > 1_100_000


def test_summary_securities_matches_published_shs_q3_2026(monkeypatch):
    # SHS Q3 2026 statement as reported by markettimes.vn and mekongasean.vn (2026-10-21):
    # operating revenue gần 1.002 tỷ; income from loans and receivables 341,1 tỷ; total assets 29.053 tỷ.
    out = _summary(monkeypatch, "securities")
    assert round(_bn(_cells(out, "Operating revenue")[1])) == 1002
    assert round(_bn(_cells(out, "Income from loans and receivables")[1]), 1) == 341.1
    assert round(_bn(_cells(out, "Total assets")[1])) == 29054  # press: 29.053 (truncated); finfo 29,053.83 bn
    assert "Margin and other loans" in out


def test_summary_insurance_matches_published_bvh_q3_2026(monkeypatch):
    # Bảo Việt Q3 2026 consolidated NPAT 834,8 tỷ as reported by vietbao.vn (Nov 2026).
    out = _summary(monkeypatch, "insurance")
    assert round(_bn(_cells(out, "Net profit after tax")[1]), 1) == 834.8
    assert "Net premium revenue" in out and "| Revenue " not in out


def test_summary_lists_items_missing_from_layout(monkeypatch):
    fake = FixtureClient("bank")
    fake.df = fake.df[fake.df["item_code"] != 413300]
    monkeypatch.setattr(fundamentals, "_client", fake)
    out = fundamentals.get_fundamentals("ACB", "2026-11-25")
    assert "Not in source data: Customer deposits" in out


def test_values_shown_in_billion_vnd_except_per_share(client):
    # live run 2026-11-25: given raw VND, the agent wrote SHS revenue 1,002 bn as "1.002 nghìn tỷ" (1000x)
    client(_rows("2026-09-30", "2026-10-30", items={21001: 1_001_990_396_188.0, 23001: 1265.0}))
    out = fundamentals.get_income_statement("SHS", "quarterly", "2026-11-25")
    assert "billion VND" in out.split("\n\n", 1)[0]
    assert "| 1,001.99 |" in out
    assert "| 1,265 (VND per share) |" in out
