import json
from pathlib import Path

import pytest

from vsi import cli
from vsi.markets import VN_ANALYSTS, vn_config


class FakePropagator:
    def get_graph_args(self, callbacks=None):  # TradingAgents 0.7.1 propagate() passes no callbacks
        return {"config": {"callbacks": callbacks or []}}


class FakeGraph:
    built = []

    def __init__(self, selected_analysts, config, callbacks):
        FakeGraph.built.append((tuple(selected_analysts), config, callbacks))
        self.config = config
        self.propagator = FakePropagator()

    def propagate(self, ticker, date):
        for handler in self.propagator.get_graph_args()["config"]["callbacks"]:
            handler.on_tool_start({}, "")
            handler.on_tool_start({}, "")
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
    monkeypatch.setenv("DNSE_API_KEY", "id")
    monkeypatch.setenv("DNSE_API_SECRET", "secret")
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: None)
    monkeypatch.setattr(cli, "install", lambda client: None)
    monkeypatch.setattr(cli.DnseClient, "instrument",
                        lambda self, sym: None if sym == "ZZZ" else {"name": sym, "market": "HOSE"})


def test_analyze_runs_graph_and_logs(tmp_path):
    cfg = vn_config() | {"results_dir": str(tmp_path)}
    out = cli.analyze("vnm", "2026-10-30", config=cfg, graph_factory=FakeGraph)
    assert out["ticker"] == "VNM.VN" and out["rating"] == "Hold"
    assert out["data_source"] == "DNSE OpenAPI"
    assert FakeGraph.built[-1][0] == VN_ANALYSTS
    line = json.loads((tmp_path / "vsi_runs.jsonl").read_text().splitlines()[-1])
    assert line["ticker"] == out["ticker"] and "tokens_in" in line
    assert out["tool_calls"] == 2


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


def test_main_requires_dnse_keys(env, monkeypatch, capsys):
    monkeypatch.delenv("DNSE_API_KEY")
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 2
    assert "DNSE_API_KEY" in capsys.readouterr().out


def test_main_refuses_unlisted_ticker_before_any_llm_run(env, monkeypatch, capsys):
    monkeypatch.setattr(cli, "TradingAgentsGraph", _raise(AssertionError("graph built")))
    assert cli.main(["analyze", "zzz", "--date", "2026-10-30"]) == 2
    assert "not listed" in capsys.readouterr().out


def test_main_reports_dnse_outage(env, monkeypatch, capsys):
    from tradingagents.dataflows.errors import VendorUnavailableError
    monkeypatch.setattr(cli.DnseClient, "instrument", _raise(VendorUnavailableError("DNSE down")))
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 1
    assert "DNSE down" in capsys.readouterr().out


def test_collect_news_cli_exit_codes(monkeypatch, tmp_path, capsys):
    monkeypatch.setenv("VSI_HOME", str(tmp_path))
    monkeypatch.setattr(cli, "collect", lambda store: {"A u": "ConnectionError", "B v": "HTTP 500"})
    assert cli.main(["collect-news"]) == 1
    monkeypatch.setattr(cli, "collect", lambda store: {"A u": "ConnectionError", "B v": 3})
    assert cli.main(["collect-news"]) == 0
    out = capsys.readouterr().out
    assert "B v: 3 new" in out and "A u: failed (ConnectionError)" in out


def test_analyze_returns_final_state_not_logged(tmp_path):
    cfg = vn_config() | {"results_dir": str(tmp_path)}
    out = cli.analyze("vnm", "2026-10-30", config=cfg, graph_factory=FakeGraph)
    assert out["final_state"] == {"final_trade_decision": "x"}
    line = json.loads((tmp_path / "vsi_runs.jsonl").read_text().splitlines()[-1])
    assert "final_state" not in line


def test_main_analyze_takes_run_lock(env, monkeypatch, tmp_path):
    events = []

    class Lock:
        def __init__(self, path):
            events.append(("lock", path))

        def __enter__(self):
            events.append("enter")

        def __exit__(self, *exc):
            events.append("exit")

    monkeypatch.setenv("VSI_HOME", str(tmp_path))
    monkeypatch.setattr(cli, "run_lock", Lock)
    monkeypatch.setattr(cli, "analyze", lambda t, d: events.append("analyze") or
                        {"ticker": "VNM.VN", "date": d, "rating": "Hold", "report_path": "r", "llm_calls": 1,
                         "tokens_in": 1, "tokens_out": 1, "seconds": 1})
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 0
    assert events == [("lock", tmp_path / "run.lock"), "enter", "analyze", "exit"]


def test_cli_bot_exits_2_on_startup_problems(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: None)
    monkeypatch.chdir(tmp_path)
    for key in ("TELEGRAM_BOT_TOKEN", "TELEGRAM_ALLOWED_CHAT_IDS"):
        monkeypatch.delenv(key, raising=False)
    assert cli.main(["bot"]) == 2
    assert "TELEGRAM_BOT_TOKEN" in capsys.readouterr().out
