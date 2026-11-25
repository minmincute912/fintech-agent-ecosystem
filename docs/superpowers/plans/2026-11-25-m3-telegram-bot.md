# M3: Telegram Bot Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `vsi bot` serves the owner's Telegram chat: `/analyze`, `/status`, `/history`, `/help`, one queued analysis at a time under a daily cap, replying with a code-built Vietnamese summary and the HTML report.

**Architecture:** Synchronous, no new dependencies. `vsi/telegram.py` is a small Bot API client on `requests` that never exposes the token; `vsi/jobs.py` keeps the queue, update offset and a cross-process run lock in SQLite/`fcntl`; `vsi/summary.py` builds the message and checks LLM price levels; `vsi/bot.py` holds the pure `handle()` command logic, the worker step and the `run()` loop with a poll thread, a worker thread and an hourly news timer.

**Tech Stack:** Python 3.13, `requests` (installed via TradingAgents), stdlib `sqlite3`, `threading`, `fcntl`, `zoneinfo`; pytest.

**Spec:** `docs/superpowers/specs/2026-11-25-m3-telegram-bot-design.md` (approved 2026-11-25).

## Global Constraints

- No new dependencies. TradingAgents v0.7.1 stays unmodified.
- New `.env` keys: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS` (comma-separated integers), optional `VSI_DAILY_RUN_CAP` (default 10).
- The bot refuses to start if the token is missing, the allowlist is empty, or `.env` is readable by group or others (`mode & 0o077 != 0`).
- The token never appears in a log record, exception string or Telegram reply.
- Telegram: `getUpdates` long poll `timeout=50`, `allowed_updates=["message"]`; text ≤ 4096 characters per message, plain text, no `parse_mode`; on HTTP 429 wait `parameters.retry_after` seconds.
- State: `$VSI_HOME/bot.sqlite`; run lock `$VSI_HOME/run.lock`; `VSI_HOME` defaults to `~/.tradingagents/vsi` (same as the news store).
- Daily cap counts bot jobs started on the Vietnam calendar day plus queued jobs; shell `vsi analyze` is not counted but takes the same run lock.
- Default analysis date = the ticker's latest DNSE bar; a bar dated today (Asia/Ho_Chi_Minh) is dropped when the request arrives before 15:05.
- Price bands: HOSE 0.07, HNX 0.10, UPCOM 0.15. Entry must be within `close × (1 ± band)`; stop-loss and target within `[low60 × (1 − band), high60 × (1 + band)]` over the last 60 sessions.
- Summary order: data block (DNSE close + band, data dates) → rating with "chưa được kiểm chứng" → checked levels → "Ý kiến agent (chưa kiểm chứng; số trong đoạn này KHÔNG được kiểm tra)" block → "Báo cáo đầy đủ: file đính kèm". Prices in thousand VND with Vietnamese decimals (`52,30`).
- A job left `running` at start-up becomes `failed` with error "bot restarted during the run" and the owner is told; it is not re-run.
- The update offset is saved before a command is executed.
- Live Telegram and paid OpenAI calls happen only in Task 7, with the owner's go.

## Review Focus

1. **Telegram down or answering 5xx/429 for minutes** → poll loop backs off (1, 2, 4 … 60 s) and resumes; a finished report stays `done_unsent` and is sent later. Pinned by `test_unsent_report_is_sent_later` (Task 5) and `test_poll_backoff_caps_at_60` (Task 6).
2. **Odd user input** (`/analyze`, `/analyze ../x`, `/analyze vnm 2026-13-01`, a future date, `/ANALYZE VNM`, `/analyze@MyBot VNM`, a photo with no text) → a Vietnamese error or help line, never a crash or a queued job. Pinned by `test_analyze_rejects_bad_input` (Task 5).
3. **Edited messages, channel posts, group chats** → ignored unless the chat is allow-listed; `allowed_updates=["message"]` plus a check on `message.chat.id`. Pinned by `test_non_allowlisted_chat_gets_nothing` (Task 5).
4. **Agent levels in VND instead of thousand VND** (e.g. 52000 vs close 52.3) → dropped with a reason, not shown. Pinned by `test_levels_in_vnd_are_dropped` (Task 3).
5. **Report too long or with characters Telegram rejects** → split at line boundaries ≤ 4096; a single line longer than 4096 is hard-split. Pinned by `test_split_text` (Task 1).

---

### Task 1: Telegram client that cannot leak the token

**Files:**
- Create: `vsi/telegram.py`
- Test: `tests/test_telegram.py`

**Interfaces:**
- Produces: `TelegramError(Exception)` with attributes `method: str`, `status: int | None`, `description: str`; `redact(text: str, secrets: Iterable[str]) -> str` (replaces each non-empty secret with `***`); `split_text(text: str, limit: int = 4096) -> list[str]`; `Telegram(token: str, session=None, sleep=time.sleep)` with `get_updates(offset: int | None, timeout: int = 50) -> list[dict]`, `send_message(chat_id: int, text: str) -> None` (sends each `split_text` chunk), `send_document(chat_id: int, path: Path, caption: str = "") -> None`.

- [ ] **Step 0:** `git checkout -b m3-telegram-bot`.
- [ ] **Step 1: Write failing tests** with a fake session recording `(url, kwargs)` and returning scripted responses:
  - `test_get_updates_params` — URL ends with `/getUpdates`; params `offset`, `timeout == 50`, `allowed_updates == '["message"]'`; request timeout > 50; returns the `result` list.
  - `test_send_message_plain_text` — `/sendMessage` with `chat_id`, `text`, no `parse_mode`; 9000 characters → 3 calls.
  - `test_send_document_multipart` — `/sendDocument`, `files={"document": ...}`, `data` has `chat_id` and `caption`.
  - `test_429_waits_retry_after` — first answer 429 `{"parameters": {"retry_after": 7}}`, then 200 → `sleep` called with 7, result returned.
  - `test_errors_never_contain_token` — token `"123:SECRET-token"`; for (a) `requests.ConnectionError` whose message contains the full URL, (b) 401 `{"description": "Unauthorized"}`, (c) 500 non-JSON: `TelegramError` raised, `str(e)`, `repr(e)` and `e.__context__` / `e.__cause__` (both `None`) contain no `SECRET`; and with `caplog` at DEBUG for all loggers, no record contains `SECRET`.
  - `test_split_text` — lines kept whole; chunks ≤ 4096; a 5000-character line is hard-split; `"".join` of chunks (with the newlines restored) equals the input.
  - `test_redact` — every secret replaced; empty secrets ignored.
- [ ] **Step 2:** Run `uv run pytest tests/test_telegram.py -v` → ImportError.
- [ ] **Step 3: Implement.** URL built as `f"https://api.telegram.org/bot{token}/{method}"` inside one private `_call(method, *, params=None, data=None, files=None, timeout=...)`; never logged. Network exception → `TelegramError(method, None, type(e).__name__)` raised outside the `except`. 429 retried up to 3 times. Non-2xx or `ok: false` → `TelegramError(method, status, redact(description, [token]))`.
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: add a minimal Telegram Bot API client that never exposes the token`.

### Task 2: Job store, offset and run lock

**Files:**
- Create: `vsi/jobs.py`
- Modify: `vsi/news.py` (extract `vsi_home() -> Path`, used by `default_store`)
- Test: `tests/test_jobs.py`

**Interfaces:**
- Produces: `Refused(Exception)` (message is the Vietnamese reply); `Job` dataclass (`id, chat_id, ticker, date, status, created_at, started_at, finished_at, error, report_path, rating, summary`); statuses `queued | running | done_unsent | done | failed`; `JobStore(path: Path)` with `enqueue(chat_id: int, ticker: str, date: str, cap: int, now: datetime) -> tuple[Job, int]` (job and queue position, raises `Refused`), `next_queued() -> Job | None`, `start(job_id: int, now: datetime)`, `finish(job_id: int, status: str, now: datetime, *, error=None, report_path=None, rating=None, summary=None)`, `active() -> list[Job]` (running + queued, oldest first), `unsent() -> list[Job]`, `runs_today(now: datetime) -> int`, `recover(now: datetime) -> list[Job]`, `get_state(key) -> str | None`, `set_state(key, value)`; `run_lock(path: Path)` context manager (blocking `fcntl.flock`); `news.vsi_home() -> Path`.

- [ ] **Step 1: Write failing tests:**
  - `test_enqueue_and_position` — two jobs → positions 1 and 2; `next_queued()` returns the first.
  - `test_duplicate_refused` — same ticker + date while queued or running → `Refused` mentioning the ticker; allowed again after `done`.
  - `test_cap_refuses_run_n_plus_1` — cap 2: two started today → third `Refused`; a job started yesterday 23:59 Vietnam time does not count; queued jobs count.
  - `test_recover_marks_running_failed` — a `running` job → `failed`, error `"bot restarted during the run"`, returned for notification.
  - `test_state_roundtrip` — offset stored and read as string.
  - `test_run_lock_is_exclusive` — a second `run_lock` from another thread blocks until the first exits (use an `Event` and a short join timeout).
- [ ] **Step 2:** Run → ImportError.
- [ ] **Step 3: Implement** with the `_db()` commit/close pattern from `vsi/news.py`; times stored as UTC ISO strings; "today" is `now.astimezone(VN_TZ).date()`.
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: SQLite job queue with daily cap, duplicate guard and run lock`.

### Task 3: Summary and level checks

**Files:**
- Create: `vsi/summary.py`
- Modify: `vsi/fundamentals.py` (add `latest_quarter`)
- Test: `tests/test_summary.py`, `tests/test_fundamentals.py`

**Interfaces:**
- Consumes: `fundamentals._client` (M2).
- Produces: `BANDS = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}`; `parse_fields(markdown: str) -> dict[str, str]` (`**Name**: value` lines; multi-line values until the next `**Name**:`); `vn_num(x: float, decimals: int = 2) -> str` (`52.3 → "52,30"`, `2126000 → "2.126.000"` with `decimals=0`); `check_levels(levels: dict[str, float | None], close: float, low60: float, high60: float, band: float) -> tuple[dict[str, float], list[str]]` (keys `entry`, `stop`, `target`; returns kept levels and one Vietnamese note per dropped level); `MarketFacts` dataclass (`exchange: str, last_bar: date, close: float, low60: float, high60: float`); `build_summary(ticker: str, analysis_date: str, facts: MarketFacts, quarter: tuple[date, date] | None, news_since: date | None, decision_md: str, trader_md: str) -> str`; `fundamentals.latest_quarter(ticker: str, as_of_date: str) -> tuple[date, date] | None` (fiscal date and created date of the latest quarter created ≤ as-of; `None` on any vendor error).

- [ ] **Step 1: Write failing tests:**
  - `test_parse_fields` — the real shapes from `schemas.render_pm_decision` / `render_trader_proposal`: Rating, Executive Summary (multi-line), Price Target `not provided`, Entry Price `52.0`, Stop Loss `49.8`.
  - `test_check_levels_boundaries` — HOSE close 52.3 (band 48.639–55.961): entry 55.97 dropped, 55.95 kept; stop at `low60 × 0.93` kept, 1% lower dropped; target above `high60 × 1.07` dropped; `None` and ≤ 0 not shown and not noted as failures.
  - `test_levels_in_vnd_are_dropped` — entry 52000 with close 52.3 → dropped, note says it is outside the band.
  - `test_summary_order_and_labels` — line order: data block, `Xếp hạng: Underweight — chưa được kiểm chứng`, levels block, `Ý kiến agent (chưa kiểm chứng; số trong đoạn này KHÔNG được kiểm tra)`, last line `Báo cáo đầy đủ: file đính kèm`; band line `biên độ HOSE ±7%: 48,64 – 55,96` for close 52.3 (computed by code, 2 decimals).
  - `test_summary_numbers_outside_opinion_block` — every number before the "Ý kiến agent" heading comes from `facts`, `quarter`, `news_since`, the date or the kept levels (collect numbers with a regex and compare against that set).
  - `test_summary_missing_fields` — decision markdown without Executive Summary or Time Horizon → "không nêu", no exception; `quarter=None` → "BCTC: không có", `news_since=None` → "tin tức: chưa thu".
  - `test_latest_quarter` (in `test_fundamentals.py`, fixture client) — corporate fixture as of 2026-11-25 → `(2026-09-30, 2026-10-30)`; as of 2026-10-29 → `(2026-06-30, 2026-07-30)`.
- [ ] **Step 2:** Run → failures.
- [ ] **Step 3: Implement.** Summary template exactly as the spec's "Summary" block with the owner's option (d) ordering.
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: Vietnamese Telegram summary with checked agent price levels`.

### Task 4: `analyze()` returns the state; shell runs take the run lock

**Files:**
- Modify: `vsi/cli.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `jobs.run_lock`, `news.vsi_home`.
- Produces: `analyze(...)` result dict gains key `"final_state"` (added after the JSONL line is written, so the log stays JSON); `main(["analyze", ...])` runs `analyze` inside `run_lock(vsi_home() / "run.lock")`.

- [ ] **Step 1: Write failing tests:** `test_analyze_returns_final_state_not_logged` (result has `final_state` equal to the fake graph's state; the JSONL line has no `final_state` key); `test_main_analyze_takes_run_lock` (patch `cli.run_lock` with a recorder; assert entered and exited around the graph run).
- [ ] **Step 2:** Run → failures.
- [ ] **Step 3: Implement.**
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: expose final state and serialise shell runs with the bot`.

### Task 5: Bot commands and worker step

**Files:**
- Create: `vsi/bot.py`
- Test: `tests/test_bot.py`

**Interfaces:**
- Consumes: Tasks 1–4; `DnseClient.instrument`, `DnseClient.daily_ohlc` (M1); `normalize_ticker` (M1); `TradingMemoryLog(config).load_entries()` (TradingAgents: dicts with `date, ticker, rating, pending, raw, alpha, holding`); `news.default_store().collected_since()` (M2).
- Produces: `HELP: str` (Vietnamese; lists the four commands and says research only, not investment advice, no orders placed); `Reply` dataclass (`chat_id: int, text: str | None = None, document: Path | None = None, job_id: int | None = None` — set on a job's last reply so the runtime marks that job `done` after a successful send); `latest_session(client, base: str, now: datetime) -> date`; `Bot(allowed: set[int], jobs: JobStore, client, cap: int, analyze=cli.analyze, history=callable, news_since=callable, now=callable)` with `handle(update: dict) -> list[Reply]` and `work_once() -> list[Reply]` (runs the next queued job under `run_lock`; returns the replies to send; `[]` when the queue is empty).

- [ ] **Step 1: Write failing tests** (fake DNSE client, fake analyze returning a result dict with `final_state`, `rating`, `report_path`):
  - `test_non_allowlisted_chat_gets_nothing` — message, edited message and a group message from a chat not in `allowed` → `[]`; with `caplog`, the log line names the chat id and contains no message text.
  - `test_analyze_queues_with_default_date` — `/analyze vnm` at 2026-11-25 10:00 VN with bars up to 2026-11-25 → queued for 2026-11-24 (today's bar dropped before 15:05); at 15:30 → 2026-11-25; reply "Đã xếp hàng VNM ngày 25/11/2026, vị trí 1".
  - `test_analyze_rejects_bad_input` — `/analyze`, `/analyze ../x`, `/analyze ZZZ` (instrument `None`), `/analyze VNM 2026-13-01`, a future date, a message with no `text` → one Vietnamese line each, nothing queued; `/ANALYZE VNM` and `/analyze@SomeBot VNM` are accepted.
  - `test_dnse_down_when_validating` — instrument raises `VendorUnavailableError` → "không kiểm tra được mã lúc này, thử lại sau", nothing queued.
  - `test_cap_reply` — `Refused` from the store becomes the reply text.
  - `test_status_reply` — running job, queued count, `runs_today/cap`, news collected-since date.
  - `test_history_reply` — two VNM entries (one pending, one settled `+3.1%`, alpha `+1.2%`, holding `5d`), newest first, at most 10; ticker with none → "chưa có lịch sử".
  - `test_free_text_gets_help` — "tại sao bearish?" → `HELP`.
  - `test_work_once_sends_summary_and_document` — job done: replies are the summary text then the `complete_report.html` document; job status `done`, rating stored.
  - `test_work_once_failure_is_reported_without_secrets` — analyze raises `RuntimeError("boom 123:SECRET-token")` with the token in env → reply contains `RuntimeError` and no `SECRET`; job `failed`.
  - `test_unsent_report_is_sent_later` — a `done_unsent` job is re-sent by `work_once()` before a new job starts.
- [ ] **Step 2:** Run → ImportError.
- [ ] **Step 3: Implement.** Commands matched on the first word lower-cased with any `@botname` suffix removed. The worker computes `MarketFacts` from `bridge.load_ohlcv(symbol, date)` (last close, last 60 sessions' low/high, last bar date) and `instrument()["market"]`; `quarter` from `fundamentals.latest_quarter`; it stores the built summary on the job (`done_unsent`), and the caller marks `done` after a successful send.
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: bot commands, queue worker and history from the memory log`.

### Task 6: `vsi bot` runtime: start-up checks, threads, polling

**Files:**
- Modify: `vsi/bot.py`, `vsi/cli.py`
- Test: `tests/test_bot.py`, `tests/test_cli.py`

**Interfaces:**
- Consumes: Task 5 `Bot`, Task 1 `Telegram`, Task 2 `JobStore`, M2 `news.collect`.
- Produces: `startup_problems(env: Mapping[str, str], env_file: Path) -> list[str]` (missing token, empty or non-integer allowlist, `.env` mode `& 0o077`); `poll_once(bot: Bot, telegram: Telegram, jobs: JobStore) -> None` (get updates from the stored offset, save `last update_id + 1` **before** handling, send replies); `backoff(failures: int) -> float` (`min(60, 2 ** (failures - 1))`, 0 failures → 0); `run() -> int` (checks, `jobs.recover()` notifications, worker thread looping `work_once`, hourly `news.collect`, poll loop until SIGINT/SIGTERM); CLI subcommand `vsi bot`.

- [ ] **Step 1: Write failing tests:**
  - `test_startup_refuses` — each of: no token, empty allowlist, `"12,abc"`, `.env` with mode 0o644 → a problem string naming it; mode 0o600 with both keys → `[]`; no problem string contains the token.
  - `test_update_handled_once_across_restart` — fake Telegram returns update 41; `poll_once` saves offset 42 before calling `handle`; a `handle` that raises still leaves offset 42; a new `JobStore` on the same file reads 42 and the next `get_updates` asks for offset 42.
  - `test_poll_backoff_caps_at_60` — `backoff(1) == 1`, `backoff(3) == 4`, `backoff(10) == 60`.
  - `test_cli_bot_exits_2_on_startup_problems` — `main(["bot"])` with an empty allowlist → 2 and the problem printed.
- [ ] **Step 2:** Run → failures.
- [ ] **Step 3: Implement.** Logging via `logging.basicConfig(level=INFO)` in `run()` only; the `urllib3` and `requests` loggers set to WARNING (they log hosts, not paths, but this keeps the URL out by construction).
- [ ] **Step 4:** Tests pass; full suite green.
- [ ] **Step 5:** Commit `feat: vsi bot runtime with start-up checks, long polling and hourly news`.

### Task 7: Live check and operations docs (owner-gated)

**Files:**
- Create: `docs/research/m3-bot-check.md`, `deploy/vsi-bot.service`
- Modify: `docs/van-hanh-vps.md`

- [ ] **Step 1:** Write `deploy/vsi-bot.service` (systemd user unit: `WorkingDirectory=%h/fintech-agent-ecosystem`, `ExecStart=%h/.local/bin/uv run vsi bot`, `Restart=on-failure`, `RestartSec=30`) and update `docs/van-hanh-vps.md`: remove the cron line; install with `systemctl --user enable --now vsi-bot` and `loginctl enable-linger`; logs via `journalctl --user -u vsi-bot`; token rotation with @BotFather `/revoke`; how to find the chat ID (send a message to the bot, then read `getUpdates` once in a browser and never paste that URL anywhere).
- [ ] **Step 2:** Ask the owner to create the bot, fill `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_CHAT_IDS` in `.env`, and approve one paid run.
- [ ] **Step 3:** Run `uv run vsi bot` locally; owner sends `/help`, `/status`, `/analyze VNM`, `/history VNM`, and a message from a second account.
- [ ] **Step 4:** Record in `docs/research/m3-bot-check.md`: each command's reply (text, with the summary pasted), the second account got nothing, the `vsi_runs.jsonl` line and cost bounds, and `grep -c` of the token's secret part in the bot's log output = 0 (count only, never print the token).
- [ ] **Step 5:** Run `git grep -nE "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" -- . ':!uv.lock'` → no matches.
- [ ] **Step 6:** Commit `research: live Telegram bot check; systemd unit and VPS guide`, then report to the owner and stop.
