# M3 design: Telegram bot for on-demand analyses

Status: draft for owner review, 2026-11-25. Builds on M1 + M2 (merged at 866ac20), the
platform spec `2026-11-03-tradingagents-vn-telegram-design.md` §4, §7, §8, §10 and
`docs/architecture.md` "Configuration and secrets".

## Intent

The owner trades Vietnamese stocks by hand, swing horizon 5–20 sessions, and wants a research
report on a ticker at the moment they consider an entry or exit, usually from a phone. Today that
means SSH to a machine and typing `vsi analyze`. M3 lets them send `/analyze VNM` in Telegram to
a bot running on a VPS and get back a short Vietnamese summary plus the full report. The bot is
for the owner only and never places orders.

## Goals

1. `vsi bot` runs a Telegram bot by long polling (no open port, no public URL).
2. Commands, from allow-listed chats only:
   - `/analyze <TICKER> [YYYY-MM-DD]` — queue one analysis; date defaults to the ticker's
     latest DNSE daily bar.
   - `/status` — running job, queue, today's runs vs the daily cap, last news collection.
   - `/history <TICKER>` — past decisions for the ticker from the TradingAgents memory log, with
     settled return and alpha vs VN-Index where settled.
   - `/help` — commands and the research-only disclaimer.
3. When an analysis finishes, the bot sends a Vietnamese summary built by code (Summary below)
   and the HTML report as a document.
4. One analysis at a time; queued jobs survive a bot restart.
5. Daily cap on started analyses (default 10, Vietnam calendar day); request N+1 is refused.
6. Vietnamese news is collected hourly by the bot process, replacing the cron line in
   `docs/van-hanh-vps.md`.
7. The bot token never appears in logs, error messages or Telegram replies (tested).

## Non-goals

- Free-text questions about a report (M5). Non-command text gets the `/help` reply.
- Evidence levels beyond "chưa được kiểm chứng" (M4).
- Push alerts, scheduled daily reports, watchlist scans.
- Inline keyboards, menus, multi-step conversations, webhooks.
- Several users, group chats, parallel analyses.
- Code-computed entry, stop-loss and position size (later, separate approval).

## Anti-goals (failure even if it "works")

- The bot answers, or reveals anything to, a chat not on the allowlist.
- The token in a log line, a traceback, a Telegram reply or a committed file.
- An LLM price level shown as if it were data: outside the labelled "Ý kiến agent" block, or a
  structured level that fails the checks shown as a number.
- A paid run beyond the cap, two analyses at once, or one Telegram message triggering two paid
  runs (for example after a restart re-reads an old update).

## Constraints

- No new dependencies: HTTP through `requests` (already installed via TradingAgents), state in
  stdlib `sqlite3`, threads from stdlib `threading`. Owner decision 2026-11-25: approach A.
- TradingAgents stays pinned and unmodified; the bot calls `vsi.cli.analyze()` and reads
  `final_state` text and the memory log.
- Secrets in `.env` only: new keys `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_IDS`
  (comma-separated integers). The bot refuses to start if the token is missing, the allowlist is
  empty, or `.env` is readable by group or others (security.md control).
- DNSE terms: data for the owner's own trading only. The allowlist holds the owner's private
  chat only; reports are not forwarded to groups.
- Telegram limits: a text message is at most 4096 characters; documents up to 50 MB. On HTTP 429
  the bot waits `parameters.retry_after` seconds.
- State file `$VSI_HOME/bot.sqlite` (same `VSI_HOME` as the news store).

## Approaches considered

| Approach | Trade-off | Decision |
|---|---|---|
| A. Own small client on `requests`: one poll thread, one worker thread, synchronous like the rest of the code | No new dependency; we write retry/backoff and offset handling (~50 lines, testable); full control of logging, so the token cannot leak through a library logger | **Chosen by owner 2026-11-25** |
| B. `python-telegram-bot` 22.8 (async, LGPL-3.0, needs `httpx`; job queue needs APScheduler) | Retries, rate limits, keyboards built in; adds 1–2 dependencies, async mixed with synchronous TradingAgents (analysis via `asyncio.to_thread`), `httpx` logs request URLs containing the token at INFO unless silenced | Rejected for M3; revisit if M5 needs multi-step dialogue |
| Webhook instead of long polling | Needs a public HTTPS endpoint and an open port | Rejected (platform spec §4) |

## Design

### Components (all in `vsi/`)

- `telegram.py` — minimal Bot API client: `get_updates(offset, timeout=50)`, `send_message(chat_id,
  text)` (splits at 4096 on line boundaries, plain text, no `parse_mode`), `send_document(chat_id,
  path, caption)`. Builds URLs internally and never logs or raises them: network errors and
  non-2xx answers become `TelegramError(method, status, description)` with the token removed
  from every string. Retries 429 after `retry_after`; network errors back off 1, 2, 4 … 60 s.
- `jobs.py` — SQLite store: `jobs(id, chat_id, ticker, date, status, created_at, started_at,
  finished_at, error, report_path, rating)`, `state(key, value)` for the update offset.
  `enqueue` refuses a duplicate (same ticker + date queued or running) and a request past the
  daily cap (counting jobs started today plus queued ones). On start-up, jobs left `running` by
  a crash become `failed` ("bot restarted during the run") and the owner is told; they are not
  re-run automatically (a re-run costs money).
- `summary.py` — builds the Vietnamese summary from `final_state["final_trade_decision"]`,
  `final_state["trader_investment_plan"]` (the rendered `**Field**: value` markdown upstream
  keeps stable for its own parsers) and vendor data. Contents below.
- `bot.py` — `run()`: start-up checks, then the poll loop in the main thread, the worker thread,
  and an hourly news-collect timer. `handle(update) -> list[Reply]` is a pure function of the
  update and the stores, so command logic is tested without the network.
- `cli.py` — new subcommand `vsi bot`.

### Flow

```
Telegram ── getUpdates (offset saved after each batch) ──► handle()
   ├─ chat not allow-listed → dropped; log "dropped update from chat <id>" (no content)
   ├─ /analyze T [D] → validate T (normalize_ticker + DNSE instrument), resolve D,
   │                    enqueue (or refuse: cap / duplicate / unlisted) → "Đã xếp hàng, vị trí N"
   ├─ /status, /history T, /help → reply
worker thread: next queued job → status running → vsi.cli.analyze(T, D)
   → summary + send_document(complete_report.html) → status done
   → on error: "Phân tích <T> lỗi: <error class and message without secrets>" → status failed
timer thread: every hour vsi.news.collect(store); failures logged, never sent to chat
```

The offset is stored before a command is executed, so a crash re-reads nothing already handled;
the trade-off is that a command arriving exactly at a crash may be lost (the owner re-sends it),
never run twice.

### Summary (plain text, Vietnamese labels)

```
VNM (HOSE) · phân tích ngày 23/11/2026
Dữ liệu: giá DNSE đến 23/11/2026 · BCTC quý 30/09/2026 (công bố ~30/10/2026) · tin tức từ 25/11/2026
Đóng cửa gần nhất 52,30 (nghìn đồng); biên độ HOSE ±7%: 48,65 – 55,95
Xếp hạng: Underweight — chưa được kiểm chứng, chỉ để nghiên cứu

Mức giá agent điền vào ô riêng (đã kiểm tra biên độ và vùng giá 60 phiên):
  Vào lệnh: không nêu · Cắt lỗ: 49,8 · Mục tiêu: không nêu
  Bỏ: <level> — <reason>

Ý kiến agent (chưa kiểm chứng; số trong đoạn này KHÔNG được kiểm tra):
  <Executive Summary from the Portfolio Manager>
  Thời gian nắm giữ: <Time Horizon or "không nêu">
Báo cáo đầy đủ: file đính kèm
```

- Data lines (close, band, data dates) come from DNSE, finfo and the news store, never from LLM
  text. Prices in thousand VND as DNSE gives them.
- Rating, executive summary and time horizon are quoted LLM output. Owner decision 2026-11-25
  (option d): the executive summary is shown, but under its own "Ý kiến agent" heading that says
  its numbers are unchecked, placed after the data and checked-level blocks. Reason: live reports
  (8 on 2026-11-25) put prices and sizing advice in the summary text, while Entry Price and Price
  Target were never filled and Stop Loss 4 times, so a "no LLM numbers" rule could not hold.
- Level checks (designer's call): band = HOSE 7%, HNX 10%, UPCoM 15% (`quant-methodology.md`
  "Daily price limit", current rules). Entry must lie within the next session's band around the
  last close. Stop-loss and target must lie within the last 60 sessions' low–high range widened
  by one band on each side. Missing, non-positive or failing levels are not shown as numbers;
  failures get a line with the reason.

### Errors

- Telegram unreachable → poll loop backs off and keeps going; the worker finishes the current
  job and retries sending its result on the next loop.
- DNSE down when validating a ticker → "không kiểm tra được mã lúc này, thử lại sau"; nothing
  queued.
- Analysis raises → job `failed`, owner told the error class and a message passed through
  `redact()` (removes the token and any `.env` value).

## Gates and checks

1. Tests (offline, fake HTTP session):
   - a non-allow-listed chat gets no reply and its content is not logged;
   - the cap refuses run N+1;
   - a duplicate request is refused;
   - an update is handled once across a simulated restart;
   - no log record, exception string or reply contains the token (log-scrub test over a full
     fake session including 401, 429 and network errors);
   - each level check passes and fails at its boundary;
   - outside the "Ý kiến agent" block, the summary contains no number taken from LLM text
     other than the checked levels; that block always carries its unchecked label.
2. Live check, owner-gated: owner creates the bot with @BotFather, puts the token and chat ID in
   `.env`, runs `vsi bot` on the current machine, sends `/help`, `/status`,
   `/analyze VNM`, `/history VNM` and a message from a second account (must get no reply).
   Record one paid run's tokens and cost in `docs/research/m3-bot-check.md`.
3. `docs/van-hanh-vps.md` updated: systemd user service for `vsi bot` (restart on failure), the
   cron line removed, how to rotate the token with @BotFather `/revoke`.

## Calls made by the designer (owner may override)

- Daily cap 10 analyses (`VSI_DAILY_RUN_CAP`), about $1–2 real cost at M2 rates, ceiling $4.5.
  The cap counts bot jobs only (started on the Vietnam calendar day, plus queued); `vsi analyze`
  from the shell is the owner's explicit choice and is not capped. One-at-a-time does cover both:
  the bot worker and `vsi analyze` take the same file lock (`$VSI_HOME/run.lock`, `fcntl.flock`);
  a shell run while the bot is running waits, a bot job waits for a shell run.
- Default analysis date = the ticker's latest DNSE bar. Whether DNSE serves an unfinished bar
  for the session in progress is unverified, so the bot drops a bar dated today (Vietnam time)
  when the request arrives before 15:05; the band check uses the same last close.
- Plain-text replies (no Markdown), so LLM text cannot break formatting or inject links.
- Crash-interrupted jobs are marked failed, not re-run.
- Hourly news collection moves into the bot; `vsi collect-news` stays for manual use.

## Left to the builder

- SQLite schema details, module names inside `vsi/`, thread shutdown on SIGTERM.
- Exact Vietnamese wording of replies, within the content above.
- How `/history` formats settled returns from `TradingMemoryLog.load_entries()`.
- `vsi.cli.analyze()` returning `final_state` as well as the result dict; a "done, not yet sent"
  job state so a Telegram outage does not lose a finished report.
