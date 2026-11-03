# M1: TradingAgents on Vietnamese Stocks (Yahoo data) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the unmodified TradingAgents graph (market analyst only) on Vietnamese tickers from a `vsi analyze VNM --date YYYY-MM-DD` command, and record the measured LLM calls, tokens and cost of each run.

**Architecture:** A small package `vsi` at the repository root depends on TradingAgents pinned at git tag `v0.7.1`. `vsi.markets` builds a Vietnam config preset from TradingAgents' `DEFAULT_CONFIG` (Yahoo vendors, VN-Index benchmark row, Vietnamese output). `vsi.cli` validates the ticker, runs `TradingAgentsGraph.propagate`, saves the report, and appends one usage line per run. No new data vendor: Yahoo is already a TradingAgents vendor.

**Tech Stack:** Python 3.11, `uv`, TradingAgents v0.7.1 (brings langgraph, langchain-openai, yfinance, pandas, python-dotenv), pytest.

**Spec:** `docs/superpowers/specs/2026-11-03-tradingagents-vn-telegram-design.md` (approved 2026-11-03 with D1–D6).

## Milestone index

CLAUDE.md forbids advancing a milestone without owner approval, so only M1 is planned in detail. Each later milestone gets its own plan once the previous one is accepted.

| Milestone | Plan |
|---|---|
| M1 Agents on VN tickers via Yahoo, cost measured | this document |
| M2 VN fundamentals + Vietnamese news (and a `vn_vendor` if Yahoo falls short) | after M1 |
| M3 Telegram bot: `/analyze`, `/status`, `/history`, `/help` | after M2 |
| M4 Pre-registered VN grid evaluation + evidence labels | after M3 |
| M5 Follow-up Q&A on the last report | after M4 |

## Global Constraints

- Research and decision support only; nothing places orders. *(CLAUDE.md)*
- TradingAgents is an unmodified pinned dependency: `tradingagents @ git+https://github.com/TauricResearch/TradingAgents.git@v0.7.1`. Never edit files under `TradingAgents/`. *(D3)*
- Data source for M1: Yahoo via TradingAgents' existing `yfinance` vendor, **research-only**, owner's own use. *(D4, owner choice 2026-11-03)*
- LLM provider: OpenAI, TradingAgents default models. `OPENAI_API_KEY` lives only in `.env` (gitignored); never printed, logged or committed. *(D1, owner choice 2026-11-03)*
- Analysts for M1: `("market",)` only. Fundamentals and news come in M2. *(spec §10 M1, D6)*
- Reports in Vietnamese: `output_language = "Vietnamese"`. *(spec §3)*
- Cost cap: `max_tokens = 4096` per LLM call; live runs (Task 5) only after the owner says go. *(spec §8)*
- New dependencies: only TradingAgents and pytest. *(CLAUDE.md: minimal dependencies)*
- Never invent prices or results; every number in the docs written here comes from a command output, cited with date. *(CLAUDE.md)*

## Review Focus

1. A ticker Yahoo does not cover (likely some HNX/UPCoM codes) → the run must report "no data" (TradingAgents' `NO_DATA_AVAILABLE` sentinel), not a made-up price. Pinned by the Task 5 run that includes one probe-failed ticker.
2. A hostile or mistyped ticker (`../x`, `VN M`, empty) → rejected before any path or prompt use. Pinned by `test_normalize_rejects_bad_input` (Task 3) and `test_main_rejects_bad_ticker` (Task 4).
3. `OPENAI_API_KEY` missing → clear message, exit code 2, no graph built, nothing billed. Pinned by `test_main_requires_api_key` (Task 4).
4. VN ticker settled against SPY because the benchmark row is missing → `resolve_benchmark` must return the VN index. Pinned by `test_vn_config_benchmark` (Task 3).
5. A future or malformed date → TradingAgents' `_validate_trade_date` raises `ValueError`; the CLI must turn it into exit 2 with the message, not a traceback. Pinned by `test_main_reports_value_error` (Task 4).

---

### Task 0: Close Phase 0 in the docs

**Files:**
- Modify: `CLAUDE.md` (section "Milestone boundaries")
- Modify: `docs/superpowers/specs/2026-11-03-tradingagents-vn-telegram-design.md` (header Status line; §10)
- Modify: `.gitignore`

- [ ] **Step 1:** In `CLAUDE.md`, replace the Phase 0–6 list under "Milestone boundaries" with the phase table from spec §10 (Phase 0 docs; Phase 1 = M1, M2; Phase 2 = M3, M4; Phase 3 = M5; later = deterministic scanner/backtester, other markets, sectors). Keep the line "Never advance to the next milestone without explicit user approval."
- [ ] **Step 2:** In the spec, set Status to `approved by owner 2026-11-03 (D1–D6)` and add under §10: `M1 choices (owner, 2026-11-03): D4 source = Yahoo via yfinance, research-only; D1 provider = OpenAI.`
- [ ] **Step 3:** Append `TradingAgents/` to `.gitignore` (it is a reference clone; the code is consumed as a pinned dependency).
- [ ] **Step 4:** Verify: `git status --short` shows `TradingAgents/` gone from untracked; `CLAUDE.md` and `docs/` still listed.
- [ ] **Step 5: Commit**

```bash
git add CLAUDE.md .gitignore docs/
git commit -m "docs: approve TradingAgents-based design and M1 plan"
```

### Task 1: Project skeleton with pinned TradingAgents

**Files:**
- Create: `pyproject.toml`
- Create: `vsi/__init__.py` (empty)
- Create: `tests/test_smoke.py`
- Create: `uv.lock` (generated)

**Interfaces:**
- Produces: importable `vsi`; `uv run pytest` works; console script `vsi = "vsi.cli:main"` (target created in Task 4).

- [ ] **Step 1: Write `pyproject.toml`**: `name = "vsi"`, `requires-python = ">=3.11"`, `dependencies = ["tradingagents @ git+https://github.com/TauricResearch/TradingAgents.git@v0.7.1"]`, `[project.optional-dependencies] dev = ["pytest>=8.0"]`, `[project.scripts] vsi = "vsi.cli:main"`, setuptools `packages = ["vsi"]`, `[tool.pytest.ini_options] testpaths = ["tests"]`.
- [ ] **Step 2: Write the smoke test**

```python
def test_tradingagents_pinned():
    import tradingagents
    assert tradingagents.__version__ == "0.7.1"

def test_stats_handler_importable():
    from cli.stats_handler import StatsCallbackHandler
    assert StatsCallbackHandler().llm_calls == 0
```

- [ ] **Step 3:** Run `uv sync --extra dev`. Expected: resolves and writes `uv.lock`, no errors.
- [ ] **Step 4:** Run `uv run pytest tests/test_smoke.py -v`. Expected: 2 passed.
- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock vsi/__init__.py tests/test_smoke.py
git commit -m "build: add vsi package pinned to TradingAgents v0.7.1"
```

### Task 2: Probe Yahoo's Vietnam coverage (gate)

**Files:**
- Create: `scripts/probe_yahoo_vn.py`
- Create: `docs/research/yahoo-vn-probe.md`

**Interfaces:**
- Produces: the verified values `VN_SUFFIX` and `VN_BENCHMARK` used by Task 3, and the list of covered exchanges.

- [ ] **Step 1: Write `scripts/probe_yahoo_vn.py`.** For each candidate symbol, call `yfinance.Ticker(sym).history(period="2y", auto_adjust=False, actions=True)` and print: symbol, row count, first date, last date, last `Close`, count of non-zero `Stock Splits`, count of non-zero `Dividends`. Equity candidates: `VNM.VN, FPT.VN, HPG.VN, SHS.VN, PVS.VN, ACV.VN, SHS.HN`. Index candidates: `^VNINDEX, ^VNINDEX.VN, VNINDEX.VN, ^VNI`. A symbol that raises or returns no rows prints `NO DATA` and the probe continues.
- [ ] **Step 2:** Run `uv run python -I scripts/probe_yahoo_vn.py` and save the full output.
- [ ] **Step 3:** Look up each equity candidate's exchange (HOSE/HNX/UPCoM) on hsx.vn or hnx.vn. Do not rely on memory; cite the page and access date, or write "exchange unverified".
- [ ] **Step 4:** Read Yahoo's terms of service, then write `docs/research/yahoo-vn-probe.md` with: the raw output, date run, exchange per ticker with its source, the chosen `VN_SUFFIX` and `VN_BENCHMARK` with the evidence, a list of which exchanges are covered, and a "Yahoo terms" line (URL, access date, what it says about personal use and automated access). Label the source **research-only**.
- [ ] **Step 5: Gate.** **STOP and report to the owner** if no HOSE candidate returns ≥ 200 rows in the last year, or if no index candidate returns data. Do not pick a substitute benchmark (such as an ETF) yourself.
- [ ] **Step 6: Commit**

```bash
git add scripts/probe_yahoo_vn.py docs/research/yahoo-vn-probe.md
git commit -m "research: probe Yahoo coverage of Vietnamese tickers"
```

### Task 3: Vietnam market preset

**Files:**
- Create: `vsi/markets.py`
- Test: `tests/test_markets.py`

**Interfaces:**
- Consumes: `VN_SUFFIX`, `VN_BENCHMARK` from `docs/research/yahoo-vn-probe.md` (Task 2); `tradingagents.default_config.DEFAULT_CONFIG`; `tradingagents.memory.settlement.resolve_benchmark(ticker: str, config: dict) -> str`; `tradingagents.dataflows.config.set_config(config: dict)`; `tradingagents.dataflows.router.route_to_vendor`, `VENDOR_METHODS`.
- Produces:
  - `VN_SUFFIX: str`, `VN_BENCHMARK: str`, `VN_ANALYSTS: tuple[str, ...] = ("market",)`
  - `normalize_ticker(raw: str) -> str`: strip and uppercase the input, append `VN_SUFFIX` if it's missing, and require the base to match `^[A-Z0-9]{3,10}$`. Anything else raises `ValueError`.
  - `vn_config() -> dict`: a deep copy of `DEFAULT_CONFIG` with the changes below

```python
data_vendors: core_stock_apis, technical_indicators, fundamental_data, news_data = "yfinance"
benchmark_map[VN_SUFFIX] = VN_BENCHMARK      # inserted, other rows kept
output_language = "Vietnamese"
llm_provider = "openai"
max_tokens = 4096
```

- [ ] **Step 1: Write the failing tests**

```python
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.memory.settlement import resolve_benchmark
from vsi.markets import VN_BENCHMARK, VN_SUFFIX, normalize_ticker, vn_config
import pytest

def test_normalize_adds_suffix():
    assert normalize_ticker(" vnm ") == "VNM" + VN_SUFFIX

def test_normalize_keeps_existing_suffix():
    assert normalize_ticker("VNM" + VN_SUFFIX) == "VNM" + VN_SUFFIX

@pytest.mark.parametrize("bad", ["", "  ", "VN M", "../x", "VNM;ls", "A" * 11, "V"])
def test_normalize_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        normalize_ticker(bad)

def test_vn_config_vendors_and_language():
    cfg = vn_config()
    for cat in ("core_stock_apis", "technical_indicators", "fundamental_data", "news_data"):
        assert cfg["data_vendors"][cat] == "yfinance"
    assert cfg["output_language"] == "Vietnamese"
    assert cfg["llm_provider"] == "openai"
    assert cfg["max_tokens"] == 4096

def test_vn_config_benchmark():
    assert resolve_benchmark("VNM" + VN_SUFFIX, vn_config()) == VN_BENCHMARK

def test_vn_config_leaves_default_untouched():
    vn_config()
    assert DEFAULT_CONFIG["output_language"] == "English"
    assert VN_SUFFIX not in DEFAULT_CONFIG["benchmark_map"]

def test_router_uses_only_yfinance(monkeypatch):
    from tradingagents.dataflows import router
    from tradingagents.dataflows.config import set_config
    set_config(vn_config())
    monkeypatch.setitem(router.VENDOR_METHODS["get_stock_data"], "yfinance", lambda *a, **k: "yahoo")
    monkeypatch.setitem(router.VENDOR_METHODS["get_stock_data"], "alpha_vantage",
                        lambda *a, **k: pytest.fail("alpha_vantage must not be called"))
    assert router.route_to_vendor("get_stock_data", "VNM.VN", "2026-01-01", "2026-02-01") == "yahoo"
```

- [ ] **Step 2:** Run `uv run pytest tests/test_markets.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.markets`.
- [ ] **Step 3:** Implement `vsi/markets.py` per the Interfaces block, using the Task 2 values. Insert the benchmark row ahead of the `""` default row; `resolve_benchmark` checks the rows in order.
- [ ] **Step 4:** Run `uv run pytest tests/test_markets.py -v`. Expected: all pass.
- [ ] **Step 5: Commit**

```bash
git add vsi/markets.py tests/test_markets.py
git commit -m "feat: add Vietnam market preset for TradingAgents"
```

### Task 4: `vsi analyze` command with a usage log

**Files:**
- Create: `vsi/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `normalize_ticker`, `vn_config`, `VN_ANALYSTS` (Task 3); `tradingagents.graph.trading_graph.TradingAgentsGraph(selected_analysts=..., config=..., callbacks=[...])` with `.propagate(ticker, date) -> (final_state, rating)` and `.save_reports(final_state, ticker) -> Path`; `cli.stats_handler.StatsCallbackHandler` (fields `llm_calls`, `tool_calls`, `tokens_in`, `tokens_out`).
- Produces:
  - `analyze(ticker: str, trade_date: str, *, config: dict | None = None, graph_factory=None) -> dict`. When `config` is None it uses `vn_config()`. When `graph_factory` is None it uses the module-level `TradingAgentsGraph`, looked up at call time so tests can patch it. It returns `{"ticker", "date", "rating", "report_path", "llm_calls", "tool_calls", "tokens_in", "tokens_out", "seconds", "model_quick", "model_deep"}`, where the two model fields come from `config["quick_think_llm"]` and `config["deep_think_llm"]`, and appends the same dict as one JSON line to `Path(config["results_dir"]) / "vsi_runs.jsonl"`.
  - `main(argv: list[str] | None = None) -> int`. It uses `argparse` with the subcommand `analyze TICKER --date YYYY-MM-DD` and calls `dotenv.load_dotenv()`. It returns 2 and prints `OPENAI_API_KEY is not set; add it to .env` when the key is missing. It also returns 2 when `analyze` raises a `ValueError`, printing that error's message. On success it prints the rating, the report path and the usage figures, and returns 0.

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path
from vsi import cli
from vsi.markets import VN_ANALYSTS, VN_SUFFIX, vn_config

class FakeGraph:
    built = []
    def __init__(self, selected_analysts, config, callbacks):
        FakeGraph.built.append((tuple(selected_analysts), config, callbacks))
        self.config = config
    def propagate(self, ticker, date):
        return {"final_trade_decision": "x"}, "Hold"
    def save_reports(self, state, ticker):
        return Path(self.config["results_dir"]) / ticker

def test_analyze_runs_graph_and_logs(tmp_path):
    cfg = vn_config() | {"results_dir": str(tmp_path)}
    out = cli.analyze("vnm", "2026-10-30", config=cfg, graph_factory=FakeGraph)
    assert out["ticker"] == "VNM" + VN_SUFFIX and out["rating"] == "Hold"
    assert FakeGraph.built[-1][0] == VN_ANALYSTS
    line = json.loads((tmp_path / "vsi_runs.jsonl").read_text().splitlines()[-1])
    assert line["ticker"] == out["ticker"] and "tokens_in" in line

def test_main_rejects_bad_ticker(monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(cli, "TradingAgentsGraph", lambda **k: (_ for _ in ()).throw(AssertionError("built")))
    assert cli.main(["analyze", "../x", "--date", "2026-10-30"]) == 2

def test_main_requires_api_key(monkeypatch, capsys):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: None)
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 2
    assert "OPENAI_API_KEY is not set" in capsys.readouterr().out

def test_main_reports_value_error(monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setattr(cli, "analyze", lambda *a, **k: (_ for _ in ()).throw(ValueError("trade_date cannot be in the future")))
    assert cli.main(["analyze", "VNM", "--date", "2099-01-01"]) == 2
    assert "future" in capsys.readouterr().out
```

- [ ] **Step 2:** Run `uv run pytest tests/test_cli.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.cli`.
- [ ] **Step 3:** Implement `vsi/cli.py` per the Interfaces block. Import `TradingAgentsGraph` and `load_dotenv` at module level so the tests can patch them. Call `normalize_ticker` before building the graph. Time the run with `time.monotonic()`.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: every test passes.
- [ ] **Step 5:** Run `uv run vsi analyze '../x' --date 2026-10-30; echo $?`. Expected: an error message and `2`.
- [ ] **Step 6: Commit**

```bash
git add vsi/cli.py tests/test_cli.py
git commit -m "feat: add vsi analyze command with per-run usage log"
```

### Task 5: Measured live runs (owner-gated: spends OpenAI credit)

**Files:**
- Create: `docs/research/m1-run-cost.md`

- [ ] **Step 1:** Ask the owner to confirm `OPENAI_API_KEY` is in `.env` and to approve three paid runs. Do not continue until they say go.
- [ ] **Step 2:** Run `uv run vsi analyze <T> --date <D>`, where `D` is the last full trading session before today. Use one probe-covered HOSE ticker, a second probe-covered ticker, and one ticker the probe returned `NO DATA` for (Review Focus 1).
- [ ] **Step 3:** For each run, check the report against the probe's data. The last close the market analyst cites must match Yahoo's close for `D`. The `NO DATA` ticker's report must say the data is unavailable and must not state a price.
- [ ] **Step 4:** Write `docs/research/m1-run-cost.md`. Include:
  - the three lines copied from `vsi_runs.jsonl`;
  - OpenAI's per-token prices for the two models, cited with URL and access date;
  - the computed cost per run;
  - the result of each Step 3 check;
  - any language problems in the Vietnamese report;
  - a projected cost for the M2 analyst set, labelled Assumption.
- [ ] **Step 5:** Run `git grep -n "sk-" -- . ':!uv.lock'`. Expected: no matches, so no key leaked into a committed file.
- [ ] **Step 6: Commit**

```bash
git add docs/research/m1-run-cost.md
git commit -m "research: record measured cost and checks of first VN agent runs"
```

- [ ] **Step 7:** Report to the owner: the results of the Step 3 checks, the cost per run, and the gaps that M2 has to close. Stop there; M2 needs approval.
