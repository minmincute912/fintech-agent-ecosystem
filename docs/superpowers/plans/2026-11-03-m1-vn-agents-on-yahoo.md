# M1: TradingAgents on Vietnamese Stocks Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

> **Revision 2, 2026-11-03.** Tasks 0–2 were done under revision 1 (Yahoo). The Task 2 probe failed its gate: Yahoo has no VN-Index history, no HNX or UPCoM stocks, and its terms forbid automated access (`docs/research/yahoo-vn-probe.md`). The owner chose SSI FastConnect Data on 2026-11-03. Tasks 3–9 replace revision 1's Tasks 3–5. The file name is kept so the execution ledger stays attached.

**Goal:** Run the unmodified TradingAgents graph (market analyst only) on Vietnamese tickers, with SSI FastConnect data, from `vsi analyze VNM --date YYYY-MM-DD`, and record the measured LLM calls, tokens and cost of each run.

**Architecture:** A small package `vsi` depends on TradingAgents pinned at git tag `v0.7.1`. `vsi.ssi` is a minimal FastConnect Data REST client. `vsi.bridge.install()` connects it to TradingAgents at runtime in three ways:
- It registers an `ssi` vendor in the data router.
- It redirects the four places where TradingAgents loads prices or company identity directly, bypassing the router. Those are the module attributes `market.load_ohlcv`, `snapshot.load_ohlcv`, `market.get_closes`/`settlement.get_closes` and `context.get_company_profile`. TradingAgents' own indicator, snapshot and settlement code then runs unchanged on SSI data.
- It disables yfinance, so that no hidden path reaches Yahoo.

`vsi.markets` holds the VN config preset. `vsi.cli` runs one analysis and logs usage.

**Tech Stack:** Python ≥3.11 (uv chose 3.13.5), `uv`, TradingAgents v0.7.1 (brings langgraph, langchain-openai, pandas, requests, stockstats, python-dotenv, yfinance), pytest.

**Spec:** `docs/superpowers/specs/2026-11-03-tradingagents-vn-telegram-design.md` (approved 2026-11-03 with D1–D6).

## Milestone index

CLAUDE.md forbids advancing a milestone without owner approval, so only M1 is planned in detail.

| Milestone | Plan |
|---|---|
| M1 Agents on VN tickers via SSI, cost measured | this document |
| M2 VN fundamentals + Vietnamese news | after M1 |
| M3 Telegram bot: `/analyze`, `/status`, `/history`, `/help` | after M2 |
| M4 Pre-registered VN grid evaluation + evidence labels | after M3 |
| M5 Follow-up Q&A on the last report | after M4 |

## Global Constraints

- Research and decision support only; nothing places orders. *(CLAUDE.md)*
- TradingAgents is a pinned dependency, `tradingagents @ git+https://github.com/TauricResearch/TradingAgents.git@v0.7.1`. Its files are never edited. Runtime redirection is allowed only through `vsi.bridge.install()`, and each redirected name has a test. *(D3; rev 2 ruling)*
- Data source: SSI FastConnect Data, base URL `https://fc-data.ssi.com.vn/`. Endpoints: `api/v2/Market/AccessToken` (POST JSON `{"consumerID", "consumerSecret"}` → `data.accessToken`), `api/v2/Market/DailyOhlc`, `api/v2/Market/DailyIndex`, `api/v2/Market/Securities` (GET, header `Authorization: Bearer <token>`). Dates are `dd/mm/yyyy`. Paging: `pageIndex` 1–10, `pageSize` 1000. *(SSI api-specs page and SSI python-fcdata `fc_md_client.py`, both read 2026-11-03)*
- SSI keys go in `.env` only, as `SSI_CONSUMER_ID` and `SSI_CONSUMER_SECRET`. Keys and tokens never appear in output, logs, exceptions or commits.
- Yahoo is never called. Its terms §2(d)(9) forbid automated access. *(yahoo-vn-probe.md)*
- No disk cache of SSI data in M1; caching is in-process only. Storage permission is unknown until the owner reads SSI's terms. *(Owner decision 1)*
- LLM: OpenAI with TradingAgents' default models. `OPENAI_API_KEY` goes in `.env` only. *(D1)*
- Analysts: `("market",)`. Reports in Vietnamese. `max_tokens = 4096`. *(spec §10, §8; D6)*
- Live SSI and OpenAI calls happen only in Tasks 8 and 9, after the owner says go.
- New dependencies: none beyond TradingAgents and pytest. `requests` comes with TradingAgents.
- Never invent prices or results. Every number written in a doc comes from command output, with its date. *(CLAUDE.md)*

## Review Focus

1. **A ticker SSI does not have, or a delisted one** → a `NoMarketDataError`, which the router turns into `NO_DATA_AVAILABLE`, never a made-up price. Pinned by `test_unknown_ticker_is_no_data` (Task 5) and the Task 9 run on a nonexistent ticker.
2. **Look-ahead**: an analysis date in the past must never see later rows. Pinned by `test_load_ohlcv_cuts_at_as_of` (Task 5).
3. **Secrets in errors**: an SSI auth failure or HTTP error message must not contain the consumer secret or the token. Pinned by `test_errors_do_not_leak_secrets` (Task 4).
4. **A hidden Yahoo call** through an unrouted path → it must fail loudly, never fetch. Pinned by `test_yahoo_is_blocked` and `test_market_tools_use_ssi` (Task 5).
5. **A hostile ticker** (`../x`, `VN M`, empty) → rejected before any path, prompt or HTTP use. Pinned by `test_normalize_rejects_bad_input` (Task 6) and `test_main_rejects_bad_ticker` (Task 7).

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


**Task 2 outcome:** the gate failed (see the revision note). The probe and its findings are committed in `4491e2a`.

### Task 3: Record the source switch in the docs

**Files:**
- Modify: `docs/superpowers/specs/2026-11-03-tradingagents-vn-telegram-design.md` (§10, the "M1 choices" line)
- Modify: `docs/research/data-sources.md` (the SSI FastConnect row: add a dated note under it)

- [ ] **Step 1:** In the spec, replace the M1 choices line with: `M1 choices (owner, 2026-11-03): D4 source = SSI FastConnect Data (Yahoo rejected: no VN-Index history, no HNX/UPCoM, ToS §2(d)(9) forbids automated access; see docs/research/yahoo-vn-probe.md); D1 provider = OpenAI.`
- [ ] **Step 2:** Under the scorecard in `data-sources.md`, add `### SSI FastConnect update (2026-11-03)`. List these facts, each cited with its URL and access date 2026-11-03:
  - Eligibility: only customers with an SSI trading account. Registration is at the counter or through a broker (`guide.ssi.com.vn/ssi-products/tieng-viet/dang-ky-dich-vu.md`).
  - Keys are created on iBoard and shown once. A fixed IP must be registered.
  - No terms of use, fees or rate limits are published on the guide pages.
  - Endpoints and the Bearer header (api-specs page; SSI `python-fcdata` `fc_md_client.py`, which has no licence and was last pushed 2024-06-05).

  End the section with: `Terms: [Owner decision needed] read the agreement signed at registration and record its storage/automation/redistribution clauses before M2.`
- [ ] **Step 3: Commit**

```bash
git add docs/
git commit -m "docs: switch M1 data source to SSI FastConnect"
```

### Task 4: SSI FastConnect client

**Files:**
- Create: `vsi/ssi.py`
- Test: `tests/test_ssi.py`

**Interfaces:**
- Consumes: `tradingagents.dataflows.errors` → `NoMarketDataError(symbol, canonical=None, detail="")`, `VendorUnavailableError(msg)`, `VendorNotConfiguredError(msg)` (also a `ValueError`).
- Produces:
  - `BASE_URL = "https://fc-data.ssi.com.vn/"`
  - `class SsiClient(consumer_id: str, consumer_secret: str, session=None, base_url: str = BASE_URL)`. `session` defaults to the `requests` module and needs only `.post(url, json=, timeout=)` and `.get(url, params=, headers=, timeout=)`.
  - `SsiClient.from_env() -> SsiClient`. Reads `SSI_CONSUMER_ID` and `SSI_CONSUMER_SECRET`. If either is missing it raises `VendorNotConfiguredError("SSI_CONSUMER_ID and SSI_CONSUMER_SECRET must be set in .env")`.
  - `daily_ohlc(symbol: str, start: datetime.date, end: datetime.date) -> pd.DataFrame` with columns `Date` (datetime64, midnight), `Open`, `High`, `Low`, `Close`, `Volume` (float), sorted by Date with no duplicate dates. It reads response fields `TradingDate` (dd/mm/yyyy), `Open`, `High`, `Low`, `Close`, `Volume`, and coerces numbers with `pd.to_numeric(errors="coerce")`.
  - `daily_index(index_id: str, start: datetime.date, end: datetime.date) -> pd.Series`: index values (field `IndexValue`, date field `TradingDate`) on a DatetimeIndex, sorted.
  - `securities() -> dict[str, dict]`: maps a symbol to `{"name": StockEnName or StockName, "market": market}`, built from markets `HOSE`, `HNX`, `UPCOM`. Cached on the instance after the first call.

**Behaviour:**
- **Token:** fetch it once, then reuse it. On HTTP 401 from a GET, fetch a new token once and retry; a second 401 raises `VendorUnavailableError`.
- **Token failure:** if the token response's `status` is not `200`, raise `VendorNotConfiguredError(f"SSI token request failed: {message}")`, where `message` is SSI's own message.
- **Request errors:** a `requests` exception or a non-2xx status other than 401 raises `VendorUnavailableError(f"SSI {path} failed: HTTP {code}")`, or `failed: {type(e).__name__}` for a `requests` exception. It never includes the URL query, the headers, the token or the secret.
- **Paging:** request `pageSize=1000` with `pageIndex=1..10` and `ascending=true`. Stop when a page has fewer than 1000 rows. If page 10 is full, log a warning. `# shortcut: 10k rows max per call (SSI paging cap), split the date range if a caller needs more`
- **Empty data:** if `daily_ohlc` gets no rows, raise `NoMarketDataError(symbol, symbol, f"SSI DailyOhlc returned no rows {start}..{end}")`. `daily_index` does the same with its own message.

- [ ] **Step 1: Write the failing tests.** Use a `FakeSession` that records each call and replies from a queue of `(status_code, json)` pairs. Its response objects have `.status_code` and `.json()`.

```python
TOKEN_OK = (200, {"status": 200, "message": "Success", "data": {"accessToken": "TKN"}})
def ohlc_page(rows): return (200, {"status": "Success", "totalRecord": len(rows), "data": rows})
ROW = lambda d, c: {"Symbol": "VNM", "Market": "HOSE", "TradingDate": d, "Time": None,
                    "Open": str(c), "High": str(c + 100), "Low": str(c - 100), "Close": str(c), "Volume": "1000", "Value": "1"}

def test_daily_ohlc_parses_and_sorts():
    s = FakeSession([TOKEN_OK, ohlc_page([ROW("31/10/2026", 56300), ROW("30/10/2026", 56000)])])
    df = SsiClient("id", "secret", session=s).daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert list(df.columns) == ["Date", "Open", "High", "Low", "Close", "Volume"]
    assert df["Date"].dt.strftime("%Y-%m-%d").tolist() == ["2026-10-30", "2026-10-31"]
    assert df["Close"].tolist() == [56000.0, 56300.0]
    get = s.calls[-1]
    assert get["headers"]["Authorization"] == "Bearer TKN"
    assert get["params"]["fromDate"] == "01/10/2026" and get["params"]["toDate"] == "31/10/2026"
    assert get["params"]["symbol"] == "VNM"

def test_daily_ohlc_pages_until_short_page():
    full = [ROW(f"{(date(2020,1,1)+timedelta(days=i)):%d/%m/%Y}", 100) for i in range(1000)]
    s = FakeSession([TOKEN_OK, ohlc_page(full), ohlc_page([ROW("01/01/2024", 100)])])
    df = SsiClient("id", "secret", session=s).daily_ohlc("VNM", date(2020, 1, 1), date(2024, 1, 1))
    assert len(df) == 1001
    assert [c["params"]["pageIndex"] for c in s.calls if c["method"] == "GET"] == [1, 2]

def test_empty_ohlc_is_no_data():
    s = FakeSession([TOKEN_OK, ohlc_page([])])
    with pytest.raises(NoMarketDataError):
        SsiClient("id", "secret", session=s).daily_ohlc("ZZZ", date(2026, 1, 1), date(2026, 2, 1))

def test_token_reused_and_refreshed_once_on_401():
    s = FakeSession([TOKEN_OK, ohlc_page([ROW("30/10/2026", 1)]), (401, {}), TOKEN_OK, ohlc_page([ROW("30/10/2026", 1)])])
    c = SsiClient("id", "secret", session=s)
    c.daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    c.daily_ohlc("VNM", date(2026, 10, 1), date(2026, 10, 31))
    assert sum(1 for x in s.calls if x["method"] == "POST") == 2

def test_errors_do_not_leak_secrets():
    for replies in ([(200, {"status": 401, "message": "Invalid consumer"})], [TOKEN_OK, (500, {})]):
        with pytest.raises(VendorError) as e:
            SsiClient("id", "S3CRET", session=FakeSession(replies)).daily_ohlc("VNM", date(2026, 1, 1), date(2026, 2, 1))
        assert "S3CRET" not in str(e.value) and "TKN" not in str(e.value)

def test_from_env_requires_keys(monkeypatch):
    monkeypatch.delenv("SSI_CONSUMER_ID", raising=False)
    with pytest.raises(VendorNotConfiguredError):
        SsiClient.from_env()

def test_daily_index_and_securities():
    idx = (200, {"status": "Success", "data": [{"IndexId": "VNINDEX", "IndexValue": "1699.62", "TradingDate": "03/11/2026"}]})
    sec = lambda rows: (200, {"status": "Success", "data": rows})
    s = FakeSession([TOKEN_OK, idx,
                     sec([{"market": "HOSE", "symbol": "VNM", "StockName": "Vinamilk", "StockEnName": "Vietnam Dairy"}]),
                     sec([]), sec([])])
    c = SsiClient("id", "secret", session=s)
    assert c.daily_index("VNINDEX", date(2026, 11, 1), date(2026, 11, 3)).iloc[-1] == 1699.62
    assert c.securities()["VNM"] == {"name": "Vietnam Dairy", "market": "HOSE"}
```

- [ ] **Step 2:** Run `uv run pytest tests/test_ssi.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.ssi`.
- [ ] **Step 3:** Implement `vsi/ssi.py` per the Interfaces and Behaviour above. Set `timeout=30` on every request.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: every test passes.
- [ ] **Step 5: Commit**

```bash
git add vsi/ssi.py tests/test_ssi.py
git commit -m "feat: add minimal SSI FastConnect Data client"
```

### Task 5: Bridge SSI into TradingAgents, and block Yahoo

**Files:**
- Create: `vsi/bridge.py`
- Test: `tests/test_bridge.py`

**Interfaces:**
- Consumes: `SsiClient` (Task 4); TradingAgents modules `tradingagents.dataflows.router` (`VENDOR_METHODS`), `tradingagents.dataflows.vendors.yahoo.market` (`load_ohlcv`, `get_closes`, `get_stock_stats_indicators_window`), `tradingagents.dataflows.vendors.yahoo.snapshot` (`load_ohlcv`, `build_verified_market_snapshot`), `tradingagents.memory.settlement` (`get_closes`), `tradingagents.agents.context` (`get_company_profile`, `_identity`, `resolve_instrument_identity`).
- Produces:
  - `INDEX_CODES = frozenset({"VNINDEX"})`
  - `base_symbol(symbol: str) -> str`: uppercase, with a trailing `.VN` removed.
  - `load_ohlcv(symbol: str, as_of_date: str, fill_gaps: bool = True) -> pd.DataFrame`. This has the same contract as TradingAgents' Yahoo `load_ohlcv`: columns `Date, Open, High, Low, Close, Volume`, and only rows with `Date <= as_of_date`. It covers `as_of_date − 5 years .. as_of_date`, rows with no Close are dropped, and the result is cached in-process with `functools.lru_cache` keyed by `(base, as_of_date)`. `# shortcut: fill_gaps ignored — SSI returns traded sessions only; revisit if a halted stock shows gaps`
  - `get_stock_data(symbol: str, start_date: str, end_date: str) -> str`. Returns `"# Stock data for {SYM} from {start} to {end}\n# Total records: {n}\n# Source: SSI FastConnect Data\n\n"` followed by the frame as CSV with `Date` as `YYYY-MM-DD`. Both ends are inclusive.
  - `get_closes(symbol: str, start_date: str, end_date: str) -> pd.Series`. Keeps Yahoo's contract: `end_date` is exclusive and the index is dates. A base in `INDEX_CODES` is read through `daily_index`.
  - `company_profile(ticker: str) -> dict`: `{"longName": name, "exchange": market}` from `securities()`, or `{}` if the ticker is unknown.
  - `install(client: SsiClient, patch=setattr, setitem=operator.setitem) -> None`. It stores the client in a module global, then calls `patch(obj, name, value)` for module attributes and `setitem(d, key, value)` for dict items:

| Object | Name | New value |
|---|---|---|
| `router.VENDOR_METHODS["get_stock_data"]` | `"ssi"` (via `setitem`) | `get_stock_data` |
| `router.VENDOR_METHODS["get_indicators"]` | `"ssi"` (via `setitem`) | `market.get_stock_stats_indicators_window` (Yahoo's indicator code, now fed by SSI) |
| `market` | `load_ohlcv` | `load_ohlcv` |
| `snapshot` | `load_ohlcv` | `load_ohlcv` |
| `market` | `get_closes` | `get_closes` |
| `settlement` | `get_closes` | `get_closes` |
| `context` | `get_company_profile` | `company_profile` |
| `yfinance` | `Ticker`, `download`, `Search` | `_yahoo_blocked`, which raises `VendorUnavailableError("Yahoo disabled: its terms forbid automated access (docs/research/yahoo-vn-probe.md)")` |

  After patching, `install` calls `context._identity.cache_clear()`.

- [ ] **Step 1: Write the failing tests.** `FakeClient` serves 300 business days ending 2026-10-30. The closes are deterministic: `50000 + 10*i`. `daily_index` serves `1600 + i`, and `securities()` returns `{"VNM": {"name": "Vietnam Dairy", "market": "HOSE"}}`. Any other symbol raises `NoMarketDataError`. A fixture installs it with `install(FakeClient(), patch=monkeypatch.setattr, setitem=monkeypatch.setitem)` and calls `set_config(vn_config_like)`, where `vn_config_like` is `DEFAULT_CONFIG` with `core_stock_apis` and `technical_indicators` set to `"ssi"`. Task 6 adds the real preset.

```python
def test_load_ohlcv_cuts_at_as_of(installed):
    df = bridge.load_ohlcv("VNM.VN", "2026-06-30")
    assert df["Date"].max() <= pd.Timestamp("2026-06-30")
    assert list(df.columns[:6]) == ["Date", "Open", "High", "Low", "Close", "Volume"]

def test_market_tools_use_ssi(installed):
    from tradingagents.dataflows.router import route_to_vendor
    from tradingagents.dataflows.vendors.yahoo.snapshot import build_verified_market_snapshot
    from tradingagents.memory import settlement
    from tradingagents.agents.context import resolve_instrument_identity
    assert "Source: SSI FastConnect Data" in route_to_vendor("get_stock_data", "VNM.VN", "2026-10-01", "2026-10-30")
    assert "rsi" in route_to_vendor("get_indicators", "VNM.VN", "rsi", "2026-10-30", 10).lower()
    assert "52990" in build_verified_market_snapshot("VNM.VN", "2026-10-30", 5)   # last close 50000+10*299
    assert settlement.get_closes("VNINDEX", "2026-10-01", "2026-10-31").iloc[-1] == 1600 + 299
    assert resolve_instrument_identity("VNM.VN")["company_name"] == "Vietnam Dairy"

def test_unknown_ticker_is_no_data(installed):
    from tradingagents.dataflows.router import route_to_vendor
    assert route_to_vendor("get_stock_data", "ZZZ.VN", "2026-10-01", "2026-10-30").startswith("NO_DATA_AVAILABLE")

def test_yahoo_is_blocked(installed):
    import yfinance
    with pytest.raises(VendorUnavailableError):
        yfinance.Ticker("VNM.VN")

def test_get_closes_end_exclusive(installed):
    s = bridge.get_closes("VNM.VN", "2026-10-28", "2026-10-30")
    assert s.index.max() < pd.Timestamp("2026-10-30")
```

- [ ] **Step 2:** Run `uv run pytest tests/test_bridge.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.bridge`.
- [ ] **Step 3:** Implement `vsi/bridge.py` per the Interfaces block. Add one comment above `install`: `# shortcut: patches TradingAgents v0.7.1 internals by name; test_bridge fails loudly if an upgrade renames them — re-check on every version bump.`
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: every test passes. If `test_market_tools_use_ssi` fails on an exact string, the assertion's value comes from the fake's formula. Read the snapshot output and fix the formula in the test, never in the code under test, and only after confirming the number really comes from the fake.
- [ ] **Step 5: Commit**

```bash
git add vsi/bridge.py tests/test_bridge.py
git commit -m "feat: bridge SSI data into TradingAgents and block Yahoo"
```

### Task 6: Vietnam market preset

**Files:**
- Create: `vsi/markets.py`
- Test: `tests/test_markets.py`

**Interfaces:**
- Consumes: `DEFAULT_CONFIG`; `resolve_benchmark(ticker, config)`; `bridge.INDEX_CODES`.
- Produces: `VN_SUFFIX = ".VN"`, `VN_BENCHMARK = "VNINDEX"`, `VN_ANALYSTS = ("market",)`. `normalize_ticker(raw: str) -> str` strips and uppercases the input, appends `.VN` if it's missing, and requires the base to match `^[A-Z0-9]{3,10}$`; anything else raises `ValueError`. `vn_config() -> dict` returns a deep copy of `DEFAULT_CONFIG` with: `data_vendors.core_stock_apis` and `technical_indicators` set to `"ssi"`; `benchmark_map` with `".VN": "VNINDEX"` inserted first; `output_language = "Vietnamese"`; `llm_provider = "openai"`; `max_tokens = 4096`. The test-only `vn_config_like` fixture in `test_bridge.py` is replaced by `vn_config()`.

- [ ] **Step 1: Write the failing tests:** `test_normalize_adds_suffix` (`" vnm "` → `"VNM.VN"`), `test_normalize_keeps_existing_suffix`, and `test_normalize_rejects_bad_input`, parametrized over `["", "  ", "VN M", "../x", "VNM;ls", "A"*11, "V"]`. Also:
  - `test_vn_config_values`: the two vendors are `"ssi"`; Vietnamese; openai; 4096.
  - `test_vn_config_benchmark`: `resolve_benchmark("VNM.VN", vn_config()) == "VNINDEX"`.
  - `test_vn_config_leaves_default_untouched`: `DEFAULT_CONFIG["output_language"] == "English"` and `".VN" not in DEFAULT_CONFIG["benchmark_map"]`.
  - `test_benchmark_is_known_index`: `VN_BENCHMARK in bridge.INDEX_CODES`.
- [ ] **Step 2:** Run `uv run pytest tests/test_markets.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.markets`.
- [ ] **Step 3:** Implement `vsi/markets.py`. In `tests/test_bridge.py`, switch the fixture to `vn_config()`.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: every test passes.
- [ ] **Step 5: Commit**

```bash
git add vsi/markets.py tests/test_markets.py tests/test_bridge.py
git commit -m "feat: add Vietnam market preset"
```

### Task 7: `vsi analyze` command with a usage log

**Files:**
- Create: `vsi/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `normalize_ticker`, `vn_config`, `VN_ANALYSTS` (Task 6); `SsiClient.from_env` (Task 4); `bridge.install` (Task 5); `TradingAgentsGraph(selected_analysts=, config=, callbacks=)` with `.propagate(ticker, date) -> (state, rating)` and `.save_reports(state, ticker) -> Path`; `cli.stats_handler.StatsCallbackHandler` (fields `llm_calls`, `tool_calls`, `tokens_in`, `tokens_out`).
- Produces:
  - `analyze(ticker: str, trade_date: str, *, config: dict | None = None, graph_factory=None) -> dict`. When `config` is None it uses `vn_config()`. When `graph_factory` is None it uses the module-level `TradingAgentsGraph`, looked up at call time. It returns `{"ticker", "date", "rating", "report_path", "llm_calls", "tool_calls", "tokens_in", "tokens_out", "seconds", "model_quick", "model_deep", "data_source": "SSI FastConnect Data"}`, where the model fields come from `config["quick_think_llm"]` and `config["deep_think_llm"]`. It also appends that dict as one JSON line to `Path(config["results_dir"]) / "vsi_runs.jsonl"`.
  - `main(argv: list[str] | None = None) -> int`. It parses `analyze TICKER --date YYYY-MM-DD`, calls the module-level `load_dotenv()`, and then:
    - returns 2 with `OPENAI_API_KEY is not set; add it to .env` if that key is missing;
    - otherwise calls `install(SsiClient.from_env())`;
    - returns 2 with the message for any `ValueError`, which includes `VendorNotConfiguredError`;
    - on success prints the rating, the report path and the usage figures, and returns 0.

- [ ] **Step 1: Write the failing tests.** These are the four tests from revision 1, kept: `test_analyze_runs_graph_and_logs`, `test_main_rejects_bad_ticker`, `test_main_requires_api_key`, `test_main_reports_value_error`. All `main` tests patch `cli.install` with a no-op and set dummy SSI env vars. Also add:

```python
def test_main_requires_ssi_keys(monkeypatch, capsys):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.delenv("SSI_CONSUMER_ID", raising=False)
    monkeypatch.setattr(cli, "load_dotenv", lambda *a, **k: None)
    assert cli.main(["analyze", "VNM", "--date", "2026-10-30"]) == 2
    assert "SSI_CONSUMER_ID" in capsys.readouterr().out
```

- [ ] **Step 2:** Run `uv run pytest tests/test_cli.py -v`. Expected: it fails with `ModuleNotFoundError: vsi.cli`.
- [ ] **Step 3:** Implement `vsi/cli.py`. Validate the ticker with `normalize_ticker` before building the graph.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: every test passes. Then run `uv run vsi analyze '../x' --date 2026-10-30; echo $?`. Expected: an error message and `2`.
- [ ] **Step 5: Commit**

```bash
git add vsi/cli.py tests/test_cli.py
git commit -m "feat: add vsi analyze command with per-run usage log"
```

### Task 8: Live SSI check (owner-gated: needs the owner's SSI keys)

**Files:**
- Create: `scripts/probe_ssi_vn.py`
- Create: `docs/research/ssi-vn-probe.md`

- [ ] **Step 1:** Ask the owner for two things. First, `SSI_CONSUMER_ID` and `SSI_CONSUMER_SECRET` in `.env`, with their fixed IP registered. Second, the storage, automation and redistribution clauses of the agreement they signed. Wait for both.
- [ ] **Step 2:** Write `scripts/probe_ssi_vn.py`. Using `SsiClient.from_env()`, for `VNM, FPT, HPG, SHS, PVS, ACV`, it prints: the market as reported by `securities()`, the row count over the last 2 years, the first and last dates, the last close, and the largest absolute one-day close change in % with its date. For `VNINDEX` it prints the row count, the first and last dates and the last value. It never prints keys or tokens.
- [ ] **Step 3:** Run `uv run python -I scripts/probe_ssi_vn.py`.
- [ ] **Step 4:** Write `docs/research/ssi-vn-probe.md` with:
  - the raw output and the date run;
  - the exchange of each ticker per SSI;
  - the price units;
  - whether the largest one-day moves exceed what normal trading allows. That would suggest the prices are not adjusted for corporate actions. Label it **Assumption** unless an official source on price bands is cited;
  - the owner's terms clauses.
- [ ] **Step 5: Gate.** STOP and report to the owner if VNINDEX has fewer than 200 rows a year, or if no HOSE ticker returns data. If VNINDEX works under a different code, fix `INDEX_CODES` and `VN_BENCHMARK` through a test first, as a ledgered ruling.
- [ ] **Step 6: Commit**

```bash
git add scripts/probe_ssi_vn.py docs/research/ssi-vn-probe.md
git commit -m "research: probe SSI FastConnect coverage of Vietnamese stocks"
```

### Task 9: Measured live runs (owner-gated: spends OpenAI credit)

**Files:**
- Create: `docs/research/m1-run-cost.md`

- [ ] **Step 1:** Ask the owner to confirm `OPENAI_API_KEY` is in `.env` and to approve three paid runs. Wait for the go.
- [ ] **Step 2:** Run `uv run vsi analyze <T> --date <D>` with `D` set to the last full session before today. Use one HOSE ticker, one HNX ticker (as reported by the Task 8 probe), and `ZZZ`, a ticker that does not exist (Review Focus 1).
- [ ] **Step 3:** Check each report:
  - The last close the analyst cites must equal SSI's close for `D` (from Task 8 or one `daily_ohlc` call).
  - `ZZZ` must report the data as unavailable, with no price.
  - The run must make no Yahoo call. A `Yahoo disabled` message in the logs is acceptable only from fail-open paths, so list where each one came from.
- [ ] **Step 4:** Write `docs/research/m1-run-cost.md` with:
  - the three `vsi_runs.jsonl` lines;
  - OpenAI's per-token prices for the two models, cited with URL and access date;
  - the cost per run;
  - the result of each Step 3 check;
  - any problems with the Vietnamese language in the reports;
  - a projected cost for the M2 analyst set, labelled Assumption.
- [ ] **Step 5:** Run `git grep -nE "sk-|SSI_CONSUMER_SECRET=." -- . ':!uv.lock'`. Expected: no matches.
- [ ] **Step 6: Commit**

```bash
git add docs/research/m1-run-cost.md
git commit -m "research: record measured cost and checks of first VN agent runs"
```

- [ ] **Step 7:** Report to the owner: the checks, the cost per run, and the gaps that M2 must close. Stop there; M2 needs approval.
