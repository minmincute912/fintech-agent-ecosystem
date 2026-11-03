import json
from pathlib import Path

import pytest

from vsi import cli
from vsi.markets import VN_ANALYSTS, vn_config


class FakeGraph:
    built = []

    def __init__(self, selected_analysts, config, callbacks):
        FakeGraph.built.append((tuple(selected_analysts), config, callbacks))
        self.config = config

    def propagate(self, ticker, date):
        return {"final_trade_decision": "x"}, "Hold"

    def save_reports(self, state, ticker):
        return Path(self.config["results_dir"]) / ticker


def _raise(exc):
    def f(*a, **k):
        raise exc
    return f


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("SSI_CONSUMER_ID", "id")
    monkeypatch.setenv("SSI_CONSUMER_SECRET", "secret")
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(cli, "install", lambda client: None)


def test_analyze_runs_graph_and_logs(tmp_path):
    cfg = vn_config() | {"results_dir": str(tmp_path)}
    out = cli.analyze("vnm", "2026-10-30", config=cfg, graph_factory=FakeGraph)
    assert out["ticker"] == "VNM.VN" and out["rating"] == "Hold"
    assert out["data_source"] == "SSI FastConnect Data"
    assert FakeGraph.built[-1][0] == VN_ANALYSTS
    line = json.loads((tmp_path / "vsi_runs.jsonl").read_text().splitlines()[-1])
    assert line["ticker"] == out["ticker"] and "tokens_in" in line


def test_main_rejects_bad_ticker(env, monkeypatch):
    monkeypatch.setattr(cli, "TradingAgentsGraph", _raise(AssertionError("graph built")))
    assert cli.main(["analyze", "../x", "--date", "2026-10-30"]) == 2


def test_main_requires_api_key(env, monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY")
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 2
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().out


def test_main_reports_value_error(env, monkeypatch, capsys):
    monkeypatch.setattr(cli, "analyze", _raise(ValueError("trade_date cannot be in the future")))
    assert cli.main(["analyze", "VNM", "--date", "2099-01-01"]) == 2
    assert "future" in capsys.readouterr().out


def test_main_requires_ssi_keys(env, monkeypatch, capsys):
    monkeypatch.delenv("SSI_CONSUMER_ID")
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 2
    assert "SSI_CONSUMER_ID" in capsys.readouterr().out
