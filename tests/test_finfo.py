from datetime import date

import pytest
import requests
from tradingagents.dataflows.errors import NoMarketDataError, VendorUnavailableError

from vsi.finfo import LAYOUTS, FinfoClient


def _row(model, item, value, fiscal="2026-09-30", created="2026-10-30 00:00:00", modified=None):
    return {"code": "VNM", "itemCode": float(item), "reportType": "QUARTER", "modelType": float(model),
            "numericValue": value, "fiscalDate": fiscal, "createdDate": created, "modifiedDate": modified or created}


class FakeResponse:
    def __init__(self, body, status_code=200):
        self._body, self.status_code = body, status_code

    def json(self):
        if isinstance(self._body, Exception):
            raise self._body
        return self._body


class FakeSession:
    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def get(self, url, params=None, timeout=None, **kw):
        self.calls.append((url, params, kw.get("headers") or {}))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


def test_statements_parse():
    body = {"data": [_row(1, 11100, 1.5e12), _row(2, 21001, 1.6e13, created="2026-10-30 00:00:00",
                                                   modified="2026-11-02 08:00:00")]}
    session = FakeSession(FakeResponse(body))
    df = FinfoClient(session).statements("vnm", "QUARTER")
    url, params, _ = session.calls[0]
    assert url == "https://api-finfo.vndirect.com.vn/v4/financial_statements"
    assert params["q"] == "code:VNM~reportType:QUARTER" and int(params["size"]) >= 2000
    assert list(df.columns) == ["model_type", "fiscal_date", "item_code", "value", "created", "modified"]
    assert df["model_type"].tolist() == [1, 2] and df["item_code"].tolist() == [11100, 21001]
    assert df["fiscal_date"].iloc[0] == date(2026, 9, 30)
    assert df["created"].iloc[1] == date(2026, 10, 30) and df["modified"].iloc[1] == date(2026, 11, 2)
    assert df["value"].iloc[1] == 1.6e13


def test_statements_cached_per_symbol_and_type():
    session = FakeSession(FakeResponse({"data": [_row(1, 1, 1.0)]}), FakeResponse({"data": [_row(1, 1, 2.0)]}))
    client = FinfoClient(session)
    client.statements("VNM", "QUARTER")
    client.statements("VNM", "QUARTER")
    client.statements("VNM", "ANNUAL")
    assert len(session.calls) == 2


@pytest.mark.parametrize("models,layout", [({1, 2, 3}, "corporate"), ({101, 102, 103}, "bank"),
                                           ({89, 90, 91}, "securities"), ({411, 412, 413}, "insurance")])
def test_layout_detection(models, layout):
    rows = [_row(m, 1, 1.0) for m in models]
    assert FinfoClient(FakeSession(FakeResponse({"data": rows}))).layout("VNM") == layout
    assert set(LAYOUTS[min(models)][1]) == models  # (name, (balance, income, cashflow))


def test_unknown_layout_is_no_data():
    client = FinfoClient(FakeSession(FakeResponse({"data": [_row(7, 1, 1.0)]})))
    with pytest.raises(NoMarketDataError):
        client.layout("VNM")


def test_item_names():
    body = {"data": [{"modelType": 1.0, "itemCode": 11100.0, "itemVnName": "Tiền", "itemEnName": "Cash",
                      "displayOrder": 20.0, "displayLevel": 2.0}]}
    session = FakeSession(FakeResponse(body))
    names = FinfoClient(session).item_names("VNM", [1, 2, 3])
    assert names == {(1, 11100): ("Tiền", "Cash", 20.0)}
    url, params, _ = session.calls[0]
    assert url.endswith("/financial_models") and params["q"] == "codeList:VNM~modelType:1,2,3"


@pytest.mark.parametrize("answer", [requests.ConnectionError("down"), FakeResponse({}, 503),
                                    FakeResponse(ValueError("not json"))])
def test_http_error_is_unavailable(answer):
    with pytest.raises(VendorUnavailableError) as e:
        FinfoClient(FakeSession(answer)).statements("VNM", "QUARTER")
    assert e.value.__context__ is None


def test_empty_is_no_data():
    with pytest.raises(NoMarketDataError):
        FinfoClient(FakeSession(FakeResponse({"data": []}))).statements("ZZZ", "QUARTER")


def test_requests_identify_the_client():
    # finfo answers 403 to python's default User-Agent (probe 2026-11-25); we send an honest one
    session = FakeSession(FakeResponse({"data": [_row(1, 1, 1.0)]}))
    FinfoClient(session).statements("VNM", "QUARTER")
    assert session.calls[0][2]["User-Agent"].startswith("vsi-research/")
