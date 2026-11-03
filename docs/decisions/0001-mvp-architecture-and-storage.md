# ADR 0001: MVP architecture and storage

- **Status:** Proposed (Phase 0, Task 5). Not in force until the owner approves it. `[Owner decision needed]`
- **Date:** 2026-10-28
- **Scope:** the MVP up to a daily Telegram shortlist and paper tracking. ML (Phase 3) and agents (Phase 4) are out of scope.
- **Details live in:** [`docs/architecture.md`](../architecture.md). This record holds only the decision, the alternatives and what is deferred.

Tag conventions follow the Phase 0 global constraints. A *designer's choice* is an architectural judgement, not a factual claim.

## Context

- The owner wants the shortest credible path to (1) a daily Telegram shortlist and (2) paper tracking, both before ML and agents. Research candidates must stay visibly separate from validated strategies (spec §11, Owner decision 3).
- **No data source is verified for a production pipeline.** No candidate's terms were shown to permit both storage and automated access (data-sources.md `## Headline findings` 1, `## Recommendation`). PyPI shows vnstock 4.0.8 as quarantined pending a security review (data-sources.md `## Headline findings` 4). The architecture must therefore be source-agnostic and must not hard-wire vnstock or any endpoint.
- **The backtester is to be built, not adapted**, as a small daily engine (github-repositories.md `## Recommendation` 1). Its build-versus-adapt choice is still an open owner decision there.
- quant-methodology.md needs homes for: the dated rules table and fill model (`## Execution and fill model`), the trial registry, pre-registration record, held-out masking loader and look counter (`## Validation design`), the risk defaults (`## Default risk settings`), and the Level 2 → 3 and demotion checks (`## Pass/fail gates`).
- Data volume is small. End-of-day bars for every listed Vietnamese stock over about 10 years are a few million rows `[Assumption]`. The owner's machine has 12 cores and 31 GB RAM (spec §3).
- On the owner's machine: Python 3.11.7 with stdlib `sqlite3` (SQLite 3.41.2) and `tomllib`; cron is installed and active; `uv`, `docker` and `psql` are present; the `duckdb` Python module and CLI are absent; the system timezone is Asia/Ho_Chi_Minh `[Fact S1]`.
- phase-0.md §8 asks whether both DuckDB and PostgreSQL are needed in the MVP.

## Options considered

**(A) Spec §8 as written.** The modular monolith with nine modules (`data`, `universe`, `features`/`labels`, `strategies`, `backtest`, `research`, `scan`, `report`, `bot`). It uses Parquet plus DuckDB for research data and DuckDB or SQLite for app state, cron or a systemd timer, and runs with `uv`. It includes an interactive Telegram bot with the eight phase-0.md §12 commands and an optional LLM wording layer.

**(A+) The phase-0.md §8 starting proposal.** This is (A) plus PostgreSQL for app metadata, FastAPI, APScheduler, aiogram or python-telegram-bot, Docker Compose, and MLflow later. It is listed because phase-0.md asks for it to be evaluated.

**(B) Lean MVP.** The same module boundaries as (A), but:
- cron runs CLI commands;
- Parquet holds market data;
- one SQLite file holds all state: trial registry, look counter, pre-registration index, evidence levels, paper ledger, job runs and send log;
- the Telegram bot is send-only, posts to an allowlist, and uses the HTTPS Bot API through the standard library;
- the paper-trading ledger is an append-only table;
- the LLM layer is dropped (Owner decision 5).

## Comparison

| Criterion | (A) Spec §8 | (A+) phase-0.md proposal | (B) Lean MVP |
|---|---|---|---|
| Time to first useful shortlist | Medium. The interactive bot (command parsing, per-user auth, long-running process) has to be built before anything is sent. | Longest. Containers, a database server, an API layer and a job framework come before the first message. | Shortest. A shortlist is a CLI run plus one HTTPS POST. Interactive commands come later and change nothing upstream. |
| Operational burden | A long-running bot process to supervise, plus cron. | A database server, containers and an API process to supervise, upgrade and secure. | Cron plus short-lived processes. Nothing listens on a port. One state file. |
| Data-loss risk | DuckDB holds state and data; one engine, one file to protect. | PostgreSQL is robust, but its volume needs dump-based backups and container-volume care. | One SQLite file plus immutable Parquet snapshots. Mitigated by WAL mode `[Assumption]`, nightly online backups copied off-disk, hash chains on every append-only table with their heads kept off-disk and in git, and the stored daily shortlist JSON (architecture.md `## Backup and recovery`). The chains are tamper-evident, not tamper-proof. |
| Effort to grow into (A) | — | — (a superset of A) | Low. The module boundaries are identical; the interactive bot is a new `bot` module calling the existing `scan`, `report` and `ops` read functions. DuckDB can later query the same Parquet files without a data migration `[Assumption: DuckDB reads Parquet in place; P1 check against the DuckDB docs]`. |
| New dependencies | duckdb, a Telegram library, a dataframe library, pyarrow | All of (A) plus a PostgreSQL driver, FastAPI and its server, APScheduler and Docker images | pandas, pyarrow, pytest only (architecture.md `## Dependencies`) |

Every row is a design judgement `[Assumption]`. No timings were measured.

## Decision

Designer's choice, pending approval: **adopt (B), the lean MVP.** `[Owner decision needed]`

1. **Module boundaries from (A) are kept**, with four changes. The fill and cost model becomes its own module, `fills`, and sizing and portfolio construction become `portfolio`, so the backtester and the paper ledger cannot diverge in either. `paper` is added. `bot` is replaced by a send-only `notify` until interactive commands are approved.
2. **Storage: Parquet plus one SQLite file. Neither DuckDB nor PostgreSQL in the MVP.** This answers phase-0.md §8.
   - Why SQLite over DuckDB for state: the state is small, transactional and append-only (ledger events, registry rows, the look counter that must increment atomically). SQLite is in the standard library already installed, so it adds no dependency `[Fact S1]`. Its stdlib online backup API makes the nightly backup a few lines `[Assumption]`. WAL mode is used `[Assumption: P1 check against the SQLite docs]`. Append-only tables use triggers plus hash chains, because triggers alone can be dropped (architecture.md `## Storage layout`).
   - **Market data is split into three physically separate partitions:** dev (before *t*_H), a sealed holdout (*t*_H to the lineage snapshot's last session T_snap) and forward (after T_snap). Only `data.store` reads Parquet. The holdout opens only through `research.holdout.unmask()` after five checks. `scan` and `paper` read only the forward path, which never counts as an H look. For its first sessions, that path takes its lookback from a price-only seed of the last W_max H sessions, and those scans are flagged `h_overlap` (architecture.md `## Data lineage and read paths`).
   - Why no DuckDB for research data: pandas plus pyarrow read the Parquet files directly, and the dataset fits in RAM `[Assumption]`. DuckDB is a candidate to add only if Phase 2 queries become slow or awkward in pandas (see Deferred).
   - Why no PostgreSQL: one user, one machine, and no concurrent writers. Cron jobs run one at a time behind a lock file. A database server adds a process, upgrades and a container volume with no MVP benefit.
3. **Data ingestion is source-agnostic.** There is one adapter per provider behind a single interface. Each adapter declares the four permissions from Owner decision 1, read from a per-source record, and its rate limit. No provider is wired in until it passes the Phase 1 P1 checks (data-sources.md `## P1 checks (consolidated)`). No provider client library, vnstock included, is installed without a supply-chain review and owner approval.
4. **Scheduling: cron**, with idempotent jobs keyed by session date and a lock file. APScheduler and systemd timers were considered. cron is already active `[Fact S1]`, and missed runs are caught by the `/health` freshness signal rather than by a scheduler feature.
5. **Telegram: send-only, with an allowlist of chat IDs, through stdlib `urllib`.** Interactive commands are scheduled in architecture.md `## Telegram scope`.
6. **Report text: deterministic Vietnamese templates through the standard library.** No LLM (Owner decision 5).
7. **Deployment: `uv run` on the owner's machine.** No Docker Compose (spec §8 default).

## Consequences

- Positive: two runtime dependencies plus pytest, no server processes, and a single file of state to back up. Every quant-methodology mechanism has one named home (architecture.md `## Where the methodology lives`).
- Negative: SQLite allows one writer at a time. That is acceptable only while all writes come from sequential cron jobs; an interactive bot that writes (for example `/watchlist`) needs the same lock or short transactions. `[Assumption]`
- Negative: until a source passes the P1 checks, the pipeline can run only on research-only data. The daily shortlist then carries a research-only data label, or is not sent, depending on owner decision O2 below.
- Negative: send-only means the owner cannot query the bot. The daily message includes the health footer instead.

## Deferred, and why

| Component | Deferred until | Reason |
|---|---|---|
| Interactive Telegram commands (`/start`, `/help`, `/health`, `/scan`, `/market`, `/watchlist`, `/analyze`, `/backtest`) | Phase 5 (staged; see architecture.md `## Telegram scope`) | They are not needed for a daily push. Each adds an input surface that must be authenticated. |
| Telegram client library (aiogram, python-telegram-bot) | Interactive commands | Sending is a single HTTPS POST. A library earns its place only with update polling and command routing. |
| LLM wording layer | Demonstrated need plus owner cost approval | Owner decision 5. |
| DuckDB | Phase 2, only if pandas queries over Parquet prove slow or awkward | The data fits in RAM `[Assumption]`. DuckDB would read the same Parquet files, so no data migration is needed `[Assumption: P1 check against the DuckDB docs]`. |
| PostgreSQL | A second concurrent writer or a second machine | No concurrency need in the MVP. `psql` being installed is not a reason. |
| FastAPI or any HTTP API | A second client beyond the CLI and Telegram | Nothing calls an API. |
| APScheduler or other job frameworks | Job dependencies that cron plus a lock cannot express | cron is active `[Fact S1]`. |
| Docker Compose | A second machine or service (spec §8) | `uv` gives reproducible environments on one host `[Assumption]`. |
| MLflow, scikit-learn | Phase 3 | ML comes after the shortlist and paper tracking (Owner decision 3). The trial registry already records runs. |
| Agent orchestration | Phase 4 | CLAUDE.md phases. |
| polars | Measured pandas bottleneck | One dataframe library is enough. |
| Fundamentals, news and intraday ingestion | A verified point-in-time source exists | data-sources.md `## Material gaps`. |
| Off-machine or cloud backup | Owner approval of a destination | No external infrastructure without approval (CLAUDE.md). |
| Kubernetes, Kafka, microservices, vector databases | Never in the MVP | CLAUDE.md. |
| Broker or order-execution integration | Never | CLAUDE.md: research and decision support only. |

## Owner decisions raised

| # | Decision | Designer's recommendation |
|---|---|---|
| O1 | Approve option (B) and the storage choice: Parquet plus SQLite, with no DuckDB or PostgreSQL in the MVP. | Approve. |
| O2 | Before any source passes the P1 checks, may research-only data feed (a) a local CLI shortlist and (b) a Telegram message to the owner's own allowlisted chat? Whether sending to oneself counts as display or redistribution under a source's terms is unknown. `[Unverified → P1 check: read each candidate's display and redistribution terms]` | (a) yes, labelled research-only; (b) no until the source's terms are read. |
| O3 | Pull a minimal slice of Phase 5 (send-only notifier) and Phase 6 (paper ledger) forward, after Phase 2 and before Phase 3. Task 7 sets the milestone numbering. | Approve. Spec §9 explains why forward calendar time cannot be compressed. |
| O4 | Paper-track Level 0–1 research candidates in a separate `research` track, so their forward results are shown but never used for promotion. | Approve, so forward evidence starts accruing. Promotion still needs Level 2 and pre-registration (quant-methodology.md `## Validation design`). |
| O5 | Approve installing pandas, pyarrow and pytest in Phase 1. | Approve when Phase 1 starts. |
| O6 | Choose a backup destination off the system disk (second disk or external drive). It is a precondition for the scheduled job (step 13) and therefore for the paper ledger (step 14). | Any local second device. No cloud service without separate approval. |
| O7 | Build-versus-adapt for the backtester (carried from github-repositories.md `## Recommendation` 1). | Build. |

## Revisit triggers

Revisit this record when any of these happens: a second writer process; a second machine; Phase 2 queries become slow in pandas; interactive commands are approved; a paid or LLM service is approved; or a verified data source imposes storage constraints (for example, no local raw copies).

## Sources

| # | Source | Publisher | Date | Accessed | Note |
|---|---|---|---|---|---|
| S1 | Local commands on the owner's machine: `which crontab sqlite3 duckdb psql uv docker`, `which rsync`, `python3 --version`, `python3 -c "import sqlite3, tomllib"`, `python3 -c "import duckdb"`, `systemctl is-active cron`, `timedatectl show -p Timezone` | Observed by the Task 5 implementer | 2026-10-28 | 2026-10-28 | Output: rsync at /usr/bin/rsync, Python 3.11.7, SQLite 3.41.2, `tomllib` imports, `duckdb` not found, cron `active`, Timezone=Asia/Ho_Chi_Minh. `python3` resolved to an Anaconda install; the `uv` project interpreter is a separate choice made in Phase 1. |
