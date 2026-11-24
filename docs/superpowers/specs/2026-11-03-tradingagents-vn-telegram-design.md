# Vietnam Stock Intelligence on TradingAgents — Revised Landing Phase Design

- Date: 2026-11-03
- Status: approved by owner 2026-11-03 (D1–D6). Supersedes parts of
  `2026-10-27-vn-stock-intelligence-design.md` (the "2026-10-27 spec") and
  `decisions/0001-mvp-architecture-and-storage.md` (ADR 0001) where listed in §9.
- Trigger: owner request of 2026-11-03 — build the application on
  TradingAgents, biased to Vietnamese stocks, extensible to other markets,
  sectors and ecosystems later, with conversation through a Telegram bot.

Labels: **Owner decision** (stated by the owner), **Designer's call**
(proposed; owner may override), **Verified** (read in code or docs on
2026-11-03), **Unverified** (must be checked before use).

## 1. Intent

Turn TradingAgents' multi-agent research pipeline into a Telegram research
assistant for HOSE, HNX and UPCoM stocks. The owner asks about a ticker in
Telegram and receives a Vietnamese research report produced by the agent
team, with every number traceable to data. *(Owner decision: TradingAgents
base, Vietnam bias, Telegram conversation)*

The 2026-10-27 intent still holds: research and decision support only, find a
real edge honestly, and say so when none is found. The agent team's rating is
an **opinion with no proven edge** until §6 evaluation shows otherwise.
*(CLAUDE.md; designer's call)*

## 2. Goals, non-goals, anti-goals

**Goals**
- `/analyze <TICKER>` in Telegram runs the TradingAgents graph on a Vietnamese
  stock and replies with a Vietnamese summary plus the full HTML report.
- Vietnamese data behind the existing TradingAgents data tools (prices,
  indicators, fundamentals, news).
- Adding another market later = adding vendor rows and a config preset, not
  new architecture (§5).
- Honest evaluation of the agents' ratings on Vietnamese stocks using
  TradingAgents' own backtest and settlement (§6).

**Non-goals**
- Order execution or broker connections. *(CLAUDE.md)*
- Intraday data, high-frequency strategies.
- Building other markets now. Only the seam for them (§5).
- A web UI, an HTTP API, multi-user accounts.

**Anti-goals** (failure even if it works)
- An LLM-written price, target or stop shown as if it were data (§7).
- A Buy/Sell rating presented with more confidence than its evaluation
  supports.
- A paid LLM or data bill the owner did not approve or cannot cap.
- Untrusted news text steering the bot into actions (§8).

## 3. What TradingAgents gives us (Verified, v0.7.1, Apache-2.0)

| Piece | Where | Use for Vietnam |
|---|---|---|
| Agent graph: 4 analysts → bull/bear debate → research manager → trader → 3-way risk debate → portfolio manager | `graph/setup.py`, `agents/` | Reuse as is. |
| Entry point `TradingAgentsGraph(config).propagate(ticker, date)` → `(final_state, rating)` | `graph/trading_graph.py:167` | The bot calls this. |
| Vendor router: `VENDOR_METHODS[method][vendor]`, chain chosen by `config["data_vendors"]`, typed no-data / unavailable sentinels that tell agents not to invent values | `dataflows/router.py` | Add a `vn` vendor (§5). |
| Point-in-time guards on dated data | `dataflows/date_window.py`, tests `test_*_lookahead.py` | Every VN vendor function must honour the same date cut-off. |
| `output_language` config | `default_config.py` | `"Vietnamese"` for reports; internal debate stays English. |
| `benchmark_map` by ticker suffix | `default_config.py` | Add a `.VN` row → VN-Index symbol (Unverified: the symbol the chosen vendor uses). |
| Decision log + settlement vs benchmark after `holding_period_days` | `memory/log.py`, `memory/settlement.py` | Records every bot run and scores it later. |
| Grid backtest of ratings (decision quality, not a portfolio sim) | `backtest.py` | §6 evaluation. |
| HTML report | `report_html.py`, `save_reports()` | Sent as a Telegram document. |
| Multi-provider LLM clients, two tiers (quick/deep) | `llm_clients/` | Provider choice is an owner decision (D1). |

**Gaps for Vietnam (Verified by grep: no `.VN`, VN-Index or Vietnam vendor in
the package):** no VN price or fundamentals source; no Vietnamese news; Reddit
and StockTwits social sources have negligible VN coverage (Assumption); FRED
macro and Polymarket are US-centric; SEC EDGAR is US-only; no price-limit,
lot-size or T+ settlement awareness.

## 4. Architecture

A modular monolith (CLAUDE.md). TradingAgents stays an **unmodified pinned
dependency**; our code lives in its own package and plugs into it.
*(Designer's call — see D3 for the fork alternative)*

```
Telegram ──long-poll──▶ bot ──▶ jobs (one run at a time, SQLite queue)
                         ▲            │
                         │            ▼
                    report_vi ◀── TradingAgentsGraph.propagate(ticker, date)
                         │            │  (config preset "vn")
                         │            ▼
                         │       router.VENDOR_METHODS ──▶ vn vendor ──▶ VN data source (D4)
                         │
                    memory log / settlement / backtest (TradingAgents, unchanged)
```

| Module (ours) | Does | Must not |
|---|---|---|
| `vn_vendor` | Implements `get_stock_data`, `get_indicators`, `get_fundamentals`, statements, `get_news` for VN tickers; registers them into `VENDOR_METHODS` at import; honours the analysis-date cut-off; raises TradingAgents' typed errors. | Return fabricated or forward-dated rows. |
| `markets` | One config dict per market (`vn` now): vendors, benchmark row, news queries, language, analysts, holding period. | Hold logic. |
| `bot` | Telegram long polling, chat-ID allowlist, commands (§7), sends text and the HTML report. | Hold business logic; log tokens. |
| `jobs` | SQLite queue of analysis requests; one worker; daily run cap; status. | Run two graphs at once (LLM cost, SQLite single writer). |
| `report_vi` | Builds the Vietnamese Telegram summary from `final_state` structured fields; labels LLM numbers (§7). | Invent or change numbers. |

Registration seam: `route_to_vendor` reads `VENDOR_METHODS` and
`TOOLS_CATEGORIES` at call time (Verified), so adding entries at import works
without editing TradingAgents. *(Designer's call)* Shortcut risk: this relies
on an internal dict; pinning the version and a test that asserts the `vn`
vendor resolves makes an upstream change fail loudly.

Unchanged from ADR 0001: SQLite for state, `uv run` on the owner's Ubuntu
machine, no Docker, no PostgreSQL, no API server, cron for scheduled jobs.
TradingAgents already depends on `langgraph-checkpoint-sqlite`, pandas,
requests and stockstats (Verified, `pyproject.toml`).

Telegram transport: **long polling** (`getUpdates`), so nothing listens on a
port and no public URL or TLS certificate is needed. *(Designer's call)*
Library vs stdlib `urllib`: designer's call is stdlib until command routing
gets painful (ADR 0001 deferral stands).

## 5. Future markets, sectors, ecosystems

A "market" is a config preset plus vendor rows. Nothing else is built for it
now. *(Designer's call)*

- New market: add vendor functions to `VENDOR_METHODS`, a `benchmark_map`
  suffix row, and a preset in `markets`. TradingAgents already resolves
  symbols per exchange (`dataflows/symbols.py`) and supports crypto via
  `asset_type="crypto"` (Verified).
- Sector view: deferred. Needs point-in-time sector membership (ICB codes are
  served by candidate VN sources, Unverified) — revisit when a sector command
  is asked for.
- "Ecosystem" (other asset classes, other chat surfaces): deferred; the bot
  calls only `propagate`, so another front end reuses the same jobs.

## 6. Evidence and evaluation

The 2026-10-27 evidence levels stay, applied to the agent team as one
"strategy":

| Level | For the agent team means |
|---|---|
| 0 Hypothesis | Agents run on VN data; ratings shown as unvalidated opinion. Default. |
| 1 Backtested | TradingAgents `run_backtest` over a pre-registered VN ticker × date grid on development dates, settled net of a cost assumption. |
| 2 Validated | The frozen config (models, prompts, analysts, rounds) passes pre-registered gates on held-out dates. |
| 3 Forward-confirmed | Live bot ratings, settled by the memory log, stay consistent with Level 2. |

Known limits *(Verified in code / Assumption)*:
- `backtest.py` scores decision quality, not a portfolio; no VN
  settlement delay (cycle Unverified), price limits, lot size or fill model. VN execution realism still
  needs the purpose-built engine from the 2026-10-27 plan before any Level 2
  claim. *(Designer's call)*
- LLM output is non-deterministic and models change; any model or prompt
  change creates a new config hash and restarts at Level 0.
- LLM pre-training may contain the backtest period ("knowledge leakage"):
  backtests on dates before the model's training cutoff are biased upward.
  Only dates after the model's cutoff count for Level 2. *(Assumption;
  strongly suspected, not measured)*
- Each grid cell is a full graph run, so evaluation cost scales with
  tickers × dates × LLM calls per run (Unverified: calls and tokens per run —
  measure in Milestone 1).

## 7. Telegram conversation

Commands *(Designer's call, MVP set)*:

| Command | Reply |
|---|---|
| `/analyze VNM` | "Queued, position N." Then the Vietnamese summary + HTML report when done. |
| `/status` | Running job, queue, today's runs vs cap, last data date. |
| `/history VNM` | Past ratings for the ticker with settled return vs VN-Index where available. |
| `/help` | Commands and the research-only disclaimer. |

Free-text follow-up questions about the last report ("why bearish?") are
**Milestone 5**, answered only from that report's saved text. *(Designer's
call; owner may pull it forward)*

Summary content: ticker, exchange, analysis date and data freshness, rating
with "chưa được kiểm chứng" (unvalidated) label unless Level 2+, executive
summary, key risks, then the agent-proposed levels.

**LLM numbers rule.** `TraderProposal.entry_price`, `stop_loss` and
`PortfolioDecision.price_target` are LLM outputs (Verified, `schemas.py`).
They are shown in a separate block titled as agent estimates, checked to be
within the stock's price-limit band and recent range, and dropped with a note
if not. Prices, returns and indicator values in the summary come from vendor
data, never from LLM text. *(Designer's call; replaces 2026-10-27 anti-goal
"an LLM producing any number" — see D1)*

## 8. Security

- Bot token and LLM keys in `.env` (gitignored). Never in logs or messages;
  the Bot API puts the token in the URL path, so URLs are never logged.
- Allowlist of owner chat IDs; all other updates are dropped silently.
- Ticker input validated against the VN listing (and TradingAgents'
  `safe_ticker_component`) before it reaches a path or a prompt.
- News and filings are untrusted text fed to LLMs. Agents have read-only data
  tools only; the bot executes nothing an agent says. Worst case of a prompt
  injection is a misleading report, which the unvalidated label covers.
- Cost cap: max runs per day and max output tokens (`max_tokens`,
  Verified config key) set in config; the job worker refuses past the cap.

## 9. What changes from the approved docs

| Approved | Now | Needs |
|---|---|---|
| Owner decision 5: no LLM, templates only | LLM agents are the core | D1 |
| Agents Phase 4, Telegram Phase 5 | Agents + interactive Telegram first | D2, CLAUDE.md edit |
| ADR 0001 send-only notifier | Interactive long-polling bot | D2 |
| Deterministic scanner + shortlist as core | Parallel or later track | D5 |
| Data source unresolved, vnstock quarantined | Still unresolved; now blocks Milestone 1 | D4 |

Unchanged: research-only, no execution, owner approval for spending, SQLite,
`uv` on Ubuntu, evidence levels, point-in-time discipline, data licensing
rules (Owner decision 1).

## 10. Owner decisions needed

| # | Decision | Designer's recommendation |
|---|---|---|
| D1 | Reverse Owner decision 5: allow an LLM provider (paid API or local Ollama) and set a monthly cost cap. | Allow; start with a cheap quick-tier model, cap runs/day; measure cost per run in M1 before raising it. |
| D2 | New phase order (below), recorded in CLAUDE.md. | Approve. |
| D3 | TradingAgents as pinned dependency vs fork. | Pinned dependency (git tag v0.7.1). Fork only if a needed change cannot go through the router or config. |
| D4 | VN data source for M1 (vnstock after supply-chain review, a broker API such as SSI FastConnect, or a paid feed) — terms per Owner decision 1. | Research-only use of one source for the owner's own chat while terms are checked, labelled research-only; same as ADR 0001 O2(a). |
| D5 | Keep the deterministic scanner/backtester track? | Keep as Phase 2b; it is needed for VN execution realism and Level 2 claims. |
| D6 | Which analysts for VN in M1. | Market + fundamentals + news; drop social (no VN coverage). |

M1 choices (owner, 2026-11-03): D4 source = SSI FastConnect Data (Yahoo rejected:
no VN-Index history, no HNX/UPCoM, ToS §2(d)(9) forbids automated access; see
docs/research/yahoo-vn-probe.md); D1 provider = OpenAI.
Revised by owner 2026-11-24: D4 source = DNSE OpenAPI instead of SSI (SSI needs
counter/broker sign-up and a fixed IP; DNSE keys are self-service online). DNSE terms
limit data to the customer's own trading and bar third-party sharing without DNSE's
written approval; see docs/research/data-sources.md "DNSE OpenAPI update".

Proposed phases (replacing CLAUDE.md's order, pending D2):

| Phase | Milestone | Done when (checkable) |
|---|---|---|
| 0 | This document + updated CLAUDE.md phases | Owner approves D1–D6. |
| 1 | M1 VN OHLCV + indicators vendor; CLI `propagate` on 3 VN tickers, market analyst only | Tests: vendor resolves via router; no row after the analysis date; NO_DATA sentinel for unknown ticker. Measured LLM calls/tokens/cost per run recorded. |
| 1 | M2 VN fundamentals (with publication date) + Vietnamese news | Look-ahead tests as in TradingAgents' `test_fundamentals_lookahead.py`. |
| 2 | M3 Telegram bot: `/analyze`, `/status`, `/history`, `/help`, allowlist, queue, cost cap | Test: non-allowlisted chat gets no reply; cap refuses run N+1; token never in logs (log-scrub test). |
| 2 | M4 Evaluation: pre-registered VN grid backtest, evidence label in replies | Registry row per run; label reads Level 0/1 correctly. |
| 3 | M5 Follow-up Q&A on the last report | Answers cite the report; out-of-report questions are declined. |
| later | Deterministic scanner/backtester (2026-10-27 plan), other markets, sectors | Separate approvals. |

## 11. Left to the builder

Package and file names, config file format, Telegram message layout within
§7, SQLite schema, test structure, how the HTML report is attached.
