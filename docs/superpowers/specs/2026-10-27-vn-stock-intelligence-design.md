# Vietnam Stock Intelligence — Product and Architecture Design

- Date: 2026-10-27
- Status: approved by owner 2026-10-27, with the decisions in §11
- Covers: product intent, MVP scope, research approach, architecture direction,
  and what Phase 0 must produce. Detailed research questions live in
  `docs/prompts/phase-0.md`; this document decides the direction that research
  serves and does not repeat it.

Labels used below:
- **Owner decision**: stated by the owner.
- **Designer's call**: proposed by the designer; the owner may override.
- **Pending research**: a default that Phase 0 must verify or replace with evidence.

## 1. Intent

The owner wants to find, validate and monitor a **robust, repeatable
swing-trading edge** in Vietnamese equities (HOSE, HNX, UPCoM), with holding
periods of 5–20 trading sessions. The aim is positive risk-adjusted returns
after realistic costs and slippage. Making money is the primary goal; learning
quant research is a by-product. *(Owner decision)*

The owner does not yet have a systematic process. The platform must help build
one from evidence rather than encode rules the owner already believes.
*(Owner decision)*

Profitability is not guaranteed. The goal is to **maximise the chance of
finding a real edge and to tell the truth when none has been found**.
*(Owner decision)*

## 2. Success, goals, non-goals, anti-goals

**Success**
- MVP: a pipeline that can test a trading hypothesis honestly, from data
  through cost-aware walk-forward backtest to an out-of-sample verdict, and
  say "passed" or "failed, because…". The daily shortlist labels every
  candidate with its evidence level. *(Designer's call)*
- Ultimate: at least one strategy passes the out-of-sample gates and then
  behaves consistently with its backtest during forward (paper) monitoring.
  *(Designer's call, following the owner's goal)*

**Goals** *(Owner decision unless marked)*
- A daily end-of-day stock scanner and a Telegram shortlist as core features.
- For each candidate: why it is shortlisted, supporting evidence, key risks,
  invalidation conditions, and 5/10/20-session scenarios.
- Realistic backtests: out-of-sample testing, appropriate benchmarks, drawdown
  analysis, liquidity limits, transaction costs, slippage.
- Configurable risk rules: liquidity floor, position concentration, stop-loss
  assumptions, cost/slippage model, maximum portfolio drawdown. Defaults are
  labelled as proposed starting points.
- Configurable position sizing. No fixed portfolio size is assumed.
- Practical about development time and data cost.

**Non-goals (MVP)**
- Order execution or any brokerage connection for placing orders. All trading
  is manual. *(Owner decision)*
- Intraday or tick data, and high-frequency strategies.
- Recommending specific VND position amounts.
- Infrastructure from the CLAUDE.md exclusion list (Kubernetes, Kafka,
  microservices, vector databases).

**Anti-goals** (failure even if the software works)
- Buy signals presented with more confidence than the evidence supports,
  especially when no strategy has passed validation.
- An attractive in-sample equity curve treated as evidence.
- Many variants tried quietly and the best one reported, with no record of
  how many were tried.
- Backtests run on today's listed stocks as if they had always existed
  (survivorship bias), or using data that was not yet available on the
  decision date (look-ahead bias).
- An LLM producing or changing any number.
- A paid API or service being charged without the owner's approval.

## 3. Constraints

- Research and decision support only. No promises of returns. *(CLAUDE.md)*
- Runs on the owner's Ubuntu machine first: 12 cores, 31 GB RAM, about
  117 GB free disk, Python 3.11, `uv`, Docker Compose v2 and the `psql`
  client installed. Ample for end-of-day data. *(Observed)*
- Free data first. Paid data only with owner approval, once its added value
  is shown. No purchases or paid accounts in Phase 0. *(Owner decision /
  CLAUDE.md)*
- Phases follow CLAUDE.md. Moving to the next phase needs explicit owner
  approval.
- Every financial calculation is deterministic, tested Python.
- Every reported number carries provenance: source, data timestamp, strategy
  or model version, assumptions.
- Telegram access is restricted to an allowlist of owner user IDs. Secrets
  live in `.env` (already gitignored) and never appear in logs or messages.
- Telegram reports are written in Vietnamese *(phase-0.md §12)*. Design and
  research documents are written in English, matching CLAUDE.md and
  phase-0.md. *(Designer's call)*
- Phase 0 rules: no dependency installs, no paid services, no infrastructure,
  no business code, no commits without explicit owner approval. Research is
  limited to documentation, public web pages and reading source code.
  *(Owner decision)*

## 4. Core concept: evidence levels

The product hinges on separating "the scanner found something" from "this
has credible evidence of an edge". Every strategy sits at exactly one level:
*(Designer's call)*

| Level | Name | Meaning |
|---|---|---|
| 0 | Hypothesis | Rules written down; not yet tested. |
| 1 | Backtested | Walk-forward backtest with costs and constraints on development data. |
| 2 | Validated | Passed the pre-registered out-of-sample gates on held-out data. |
| 3 | Forward-confirmed | Paper monitoring after validation is consistent with the backtest. |

Rules:
- **Pre-registration.** A strategy's rules, parameters and pass/fail gates are
  frozen and recorded *before* it touches the held-out test period. Phase 0
  defines the default gates and justifies each threshold. Expected topics:
  net excess return versus benchmark after costs, a significance measure that
  accounts for the number of trials, stability across sub-periods and
  liquidity buckets, maximum drawdown, and capacity at the configured
  position size. *(Designer's call; thresholds pending research)*
- **Trial registry.** Every backtest run is logged with its config hash, data
  version, code version and results. The count of trials feeds the
  multiple-testing adjustment. Logs are append-only: runs are never deleted.
  *(Designer's call)*
- **Held-out period.** A final slice of history stays untouched until a
  strategy is frozen. Each look at it is recorded and counts against that
  strategy. Its length is set in Phase 0 based on how much history is
  available. *(Designer's call; length pending research)*
- **Demotion.** If forward monitoring diverges from the backtest beyond a
  pre-set tolerance, the strategy drops a level and the shortlist says so.
  *(Designer's call)*

## 5. Daily scanner and Telegram shortlist

Runs after each session close on end-of-day data. *(Owner decision)*

The report has two clearly separated sections: *(Designer's call)*
1. **Validated signals**: only from Level 2+ strategies.
2. **Research candidates (chưa được kiểm chứng / not yet validated)**: from
   Level 0–1 strategies, plainly labelled as having no proven edge.

If no strategy is at Level 2+, the report says so first and links to the
latest research summary: what failed, why, and the next research directions.
It never fills the gap with made-up signals. *(Owner decision)*

Each candidate shows:
- ticker, exchange, as-of timestamp and data freshness
- strategy name, version and evidence level
- horizon(s) and score, with what the score means
- why shortlisted: the features that triggered it, with values
- key risks and liquidity flags, including missing-data warnings
- invalidation conditions, stated as price or indicator levels computed
  deterministically
- 5/10/20-session scenarios

**Scenarios** are the historical distribution of outcomes for that strategy's
past signals: median, spread, hit rate and worst-case percentile at each
horizon, net of costs. They are not price targets. *(Designer's call)*

Commands follow phase-0.md §12 (`/start`, `/help`, `/market`, `/scan`,
`/analyze`, `/backtest`, `/watchlist`, `/health`). Phase 0 refines their
behaviour; Telegram is not built in Phase 0.

## 6. Research approach

**Market facts to verify in Phase 0** *(Pending research; not to be assumed)*:
price-limit bands per exchange, settlement cycle and when bought shares can
be sold, lot and tick sizes, fees and taxes, foreign-ownership limits,
trading calendar and suspensions.

**Execution model.** The signal uses data from session *t*, including the
close. The base case enters at the session *t+1* opening auction (ATO); the
5/10/20-session clock starts at entry. Stocks at their limit-up price at the
open are assumed unfillable, and fills at the open are capped by auction
volume (fill model detailed in Phase 0; an opening price is not a guaranteed
fill). Every backtest also reports results with entry
at the *t+1* close (ATC) as a sensitivity check, so an edge that only exists
at one fill assumption shows up. Exits follow the same rules. *(Designer's
call. It assumes the owner can place orders before the open on most days;
see §11.)*

**Long-only.** The working assumption is that retail investors cannot
practically short Vietnamese stocks, so strategies are long-only with a cash
option. *(Designer's call; pending research)*

**Hypothesis backlog.** Phase 0 ranks these by plausibility, published
evidence for Vietnam or similar markets, and data feasibility. The list is
the designer's starting point, not a claim that any of them works.
- relative strength or momentum versus VN-Index or a sector
- short-term reversal after large moves or limit-down days
- breakouts confirmed by volume or traded value
- trend filters on the market index (when to be in cash)
- foreign or proprietary trading net flows, if historical data exists
- sector rotation
- earnings-related drift, only if publication timestamps are reliable
- low-volatility or quality tilts, as a slower baseline

**Progression.** Benchmarks and simple rules come first. Regularised linear
models come next, and tree models only if they beat the simple rules out of
sample (phase-0.md §7). ML is not a goal in itself. *(Owner's brief)*

**Targets.** A default target (expected: cross-sectional ranking of
benchmark-relative forward returns, net of costs) is chosen in Phase 0, with
handling of overlapping labels. *(Pending research)*

**Universe.** Membership is rebuilt for each historical date from data
available at that date. If the data source lacks delisted stocks, every
backtest carries a visible survivorship-bias warning, and Phase 0 reports
whether paid data would close that gap. *(Designer's call)*

## 7. Risk and cost settings

All settings live in one config file. Every default carries a "proposed
default" label and the reason behind it. *(Owner decision / designer's call)*

Settings:
- minimum average traded value
- maximum share of a stock's daily traded value that one order may take
- maximum position weight and maximum number of positions
- maximum sector weight
- stop-loss assumption (none, fixed %, volatility-based) used in backtests
  and in invalidation levels
- commission, tax and slippage model
- portfolio drawdown limit that triggers a "risk-off" flag in reports

Default values come from Phase 0 research (verified fees and taxes, liquidity
distributions) and are not invented here.

- **Capacity without a fixed portfolio size:** liquidity and capacity results
  are reported over a grid of notional position sizes, which Phase 0 proposes.
  A strategy's verdict states the largest size at which it still passes.
  *(Designer's call)*
- **Commission:** the default is a conservative rate from the upper range of
  published Vietnamese broker fee schedules. The owner's actual broker rate is
  an optional setting. *(Designer's call)*

## 8. Architecture direction

A modular monolith: one Python package, one repository. *(CLAUDE.md;
designer's call on the details below, all pending Phase 0 confirmation)*

```
data sources ─▶ ingest ─▶ validate ─▶ store (Parquet + DuckDB)
                                         │
                universe ◀───────────────┤
                features / labels ◀──────┤
                                         ▼
           strategies ─▶ backtest ─▶ trial registry ─▶ evidence levels
                                         │
                                         ▼
                        daily scan ─▶ report builder ─▶ Telegram bot
                                         │
                              (optional) LLM wording layer
```

| Module | Responsibility | Must not |
|---|---|---|
| `data` | Fetch, validate and store raw and adjusted end-of-day data with source and timestamps. | Compute features or signals. |
| `universe` | Point-in-time eligible stock list. | Use future listings. |
| `features`, `labels` | Deterministic features stamped with when they became available; forward labels for research only. | Leak labels into scanning. |
| `strategies` | Pure rule definitions and their parameters. | Fetch data or call an LLM. |
| `backtest` | Simulate fills with limits, costs, liquidity, settlement. | Optimise silently. |
| `research` | Trial registry, walk-forward runs, gates, evidence levels, research summaries. | Delete trials. |
| `scan` | Run Level 0+ strategies on the latest data and build structured candidates. | Invent missing values. |
| `report` | Turn structured candidates into Vietnamese text. | Change numbers. |
| `bot` | Telegram commands, allowlist, formatting. | Hold business logic. |

Defaults:
- **Storage:** Parquet files plus DuckDB for research data. For the MVP's
  small app state (watchlists, trial registry, job runs), DuckDB or SQLite is
  likely enough and PostgreSQL can be skipped. Phase 0 confirms or rejects
  this. *(Designer's call)*
- **Scheduling:** cron or a systemd timer. No job framework. *(Designer's call)*
- **Deployment:** run directly with `uv` on the owner's machine. Docker
  Compose waits until there is a second machine or service to deploy.
  *(Designer's call)*
- **Backtesting:** a small purpose-built engine is likely needed for
  Vietnam-specific rules. Phase 0 checks whether vectorbt, qlib or others can
  be reused. *(Pending research)*
- **AI agents:** none before Phase 4. Shortlist text works without an LLM
  using templates. Phase 4 assesses whether an LLM layer that only rewords
  provided facts (with a check that every number matches the source) adds
  value. Any paid LLM API needs owner approval. *(Designer's call)*

## 9. Roadmap emphasis

The CLAUDE.md phases stand. Two recommendations to serve the edge-finding
goal: *(Designer's call; changing phase order needs owner approval)*
1. Phase 2 includes the trial registry, evidence levels, held-out discipline
   and a command-line daily scan. It ends with a research summary of each
   tested hypothesis.
2. Forward monitoring needs calendar time that cannot be shortened. So once
   any strategy reaches Level 2, a minimal daily Telegram shortlist and paper
   tracking should start **before** ML (Phase 3) and agents (Phase 4).
   *(Open question: see §11.)*

## 10. Phase 0 plan

Phase 0 ends with documents and a completion report, then stops. Phase 0 does
not install anything. Facts that only a live test could confirm (for example,
whether a source really includes delisted tickers) are marked
**unverified – needs a Phase 1 check**, and Phase 1 starts with that check.

**Evidence rule for every Phase 0 document.** Each claim is tagged as one of:
- **Fact**: backed by a cited source (link plus access date). Official
  sources (exchanges, regulators, provider terms and pricing pages, project
  repositories) take priority.
- **Assumption**: no source found; the reason is stated.
- **Owner decision needed**

Provider capabilities, prices, limits and licences are never filled in from
memory.

| # | Task | Deliverable | Done when |
|---|---|---|---|
| 1 | **Market rules**: price limits, settlement and sellable date, lot and tick sizes, fees and taxes, foreign-ownership limits, trading sessions (ATO/continuous/ATC), calendar, suspensions, delisting rules, for HOSE/HNX/UPCoM. | `quant-methodology.md` §Market rules | Every rule cites an official source with its date, or is marked unverified. |
| 2 | **Data sources**: free candidates (vnstock and the endpoints it wraps, exchange sites, broker data APIs) and paid candidates found by research. Each is assessed on the phase-0.md §5 fields. | `research/data-sources.md` | Scorecard covers every candidate on every field (or says "unknown"). It explicitly answers: delisted coverage, how prices are adjusted, point-in-time fundamentals, and terms on storage, automation and model training. It ends with a primary and fallback recommendation and a cost table with links. |
| 3 | **Open-source projects**: vnstock (both repos), qlib, vectorbt, freqtrade, plus others found. Assessed on the phase-0.md §4 criteria by reading repos and docs only. | `research/github-repositories.md` | Each project has its latest release date, licence and activity taken from the repo, and a verdict (reuse/adapt/study/reject) with a reason. |
| 4 | **Quant method**: universe construction, default target and labels, execution model (§6), walk-forward splits and held-out length based on the verified history depth, pre-registered gates with numeric thresholds and their rationale, metric formulas, cost and slippage model, capacity grid, ranked hypothesis backlog. | `quant-methodology.md` | A builder could implement the backtester and gates without asking anything; every threshold has a stated reason. |
| 5 | **Architecture vs lean MVP**: compare §8 against the leanest path to a useful daily Telegram shortlist plus paper-tracking ledger (cron, CLI, a single file database, a send-only bot). Choose the storage option and decide which modules to defer. | `architecture.md`, decision record(s) | A decision record names the chosen option, the alternatives, and what is deferred and why. A diagram and repo layout are included. |
| 6 | **Agents, prompts, security**: when an LLM is justified, the number-check rule, prompt-injection boundaries, secrets, Telegram allowlist, how paid-API usage is capped, MCP use at development time vs runtime. | `agent-design.md`, `security.md` (short) | Every phase-0.md §9–13 item is addressed or explicitly deferred. |
| 7 | **PRD and roadmap**: scope, evidence levels, report format with one Vietnamese mock-up, Phase 1+ milestones with testable acceptance criteria and the early shortlist/paper path. | `PRD.md`, `roadmap.md` | Each milestone has pass/fail criteria that can be checked. |
| 8 | **Completion report**: the 12 items from phase-0.md §15, split into Facts / Assumptions / Owner decisions. | In chat (and `roadmap.md`) | Owner can approve or reject Phase 1 from it alone. |

Order: tasks 1–3 first (independent). Task 4 depends on 1–2, task 5 on 2–4,
and tasks 6–8 come last. Documents stay uncommitted until the owner approves.

## 11. Owner decisions (2026-10-27)

1. **Data licensing.** Free data is not assumed to be unrestricted. Sources
   with unclear terms are researched and their limitations flagged. None is
   chosen for the primary production pipeline until its permitted uses are
   verified. Each source is assessed separately on four permissions: public
   access, storage, automated access, and use for redistribution or model
   training.
2. **Paid data budget:** zero to start. Free and paid options are both
   researched, and a paid source is recommended only if it closes a clear,
   material gap. Nothing is bought or activated without explicit approval.
3. **Roadmap:** approved. A useful daily Telegram shortlist and paper tracking
   come early, before ML and multi-agent work. Research candidates stay
   visibly separate from validated strategies.
4. **Execution:** baseline entry at the next session with an alternative
   execution-price sensitivity test (§6). Phase 0 verifies order timing,
   price limits, liquidity and fill assumptions from reliable sources. An
   opening price is **not** assumed to guarantee a fill: the fill model must
   account for auction mechanics, limit-locked stocks and volume.
5. **Report text:** deterministic templates only. Paid AI services and
   AI-generated investment commentary are deferred until there is a
   demonstrated need and the owner approves the cost.

## 12. Left to the builder

- Library choices within the stated stack, file layout inside modules,
  config format, and test structure.
- Exact report wording and layout, within §5's content requirements.
- How the trial registry is stored, as long as it is append-only and
  queryable.
