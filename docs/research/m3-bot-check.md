# M3 live bot check — 2026-11-25

Plan: `docs/superpowers/plans/2026-11-25-m3-telegram-bot.md`, Task 7. Branch `m3-telegram-bot` at f9f3595.
The bot ran on the development machine (`uv run vsi bot`), not on the VPS. Facts below come from the
bot log, `$VSI_HOME/bot.sqlite` and `vsi_runs.jsonl`; replies on the phone were checked by the owner.

## Start-up

```
10:18:33 INFO vsi.bot: bot started; allowed chats: 1; daily cap: 10
10:18:35 INFO vsi.bot: news collected: 50 new
```

All start-up checks passed (token, allowlist, OpenAI and DNSE keys, `.env` mode 600).

## Commands

| Command | Result |
|---|---|
| `/help`, `/status` | Owner reported done; the bot does not log reply text. |
| `/analyze VNM` | Job 1 queued 10:30:09, started 10:30:13, `done_unsent` 10:32:38, `done` 10:32:40 (summary and report delivered). |
| `/history VNM` | Owner reported done; no log line by design. |
| Message from a second account | Not tested: the log has no `dropped update` line. The allowlist is covered by `tests/test_bot.py`. |

Default date: the bot chose **23/11/2026**. DNSE has no bar for 24/11 for VNM, FPT, HPG or SHS; the owner
confirmed 24/11 was a Vietnamese public holiday. The date comes from DNSE bars, so no holiday calendar is
needed.

## Summary sent (verbatim)

```
VNM (HOSE) · phân tích ngày 23/11/2026
Dữ liệu: giá DNSE đến 23/11/2026 · BCTC quý 30/09/2026 (tạo 30/10/2026) · tin tức thu từ 25/11/2026
Đóng cửa gần nhất 52,30 (nghìn đồng); biên độ HOSE ±7%: 48,64 – 55,96
Xếp hạng: Underweight — chưa được kiểm chứng, chỉ để nghiên cứu

Mức giá agent điền vào ô riêng (đã kiểm tra biên độ và vùng giá 60 phiên):
  Vào lệnh: 52,30 · Cắt lỗ: không nêu · Mục tiêu: không nêu
```

followed by the agent's Executive Summary under its unchecked heading. "tin tức thu từ 25/11" is the
first collection of this news store; the RSS feeds still carried items published on 23/11, and the news
analyst cited one (Vietstock, 23/11).

## Run log line

```json
{"ticker": "VNM.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 16, "tool_calls": 22,
 "tokens_in": 105653, "tokens_out": 19546, "seconds": 143.5, "model_quick": "gpt-6-luna",
 "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
```

Cost bounds (prices as in `m1-run-cost.md`; the log has totals, not tokens per model): all tokens at
`gpt-6-luna` $0.020, all at `gpt-6-sol` $0.407. Fact: this run cost at most $0.41.

## Token exposure

- Bot log: 0 matches for `[0-9]{8,10}:[A-Za-z0-9_-]{30,}`, 0 lines containing `api.telegram`.
- `~/.tradingagents` (reports, logs, SQLite): 0 files match the pattern.
- `git grep -nE "[0-9]{8,10}:[A-Za-z0-9_-]{30,}" -- . ':!uv.lock'`: no matches.

## Expected warnings

`Vendor 'vsi' unavailable for get_insider_transactions / get_macro_indicators / get_prediction_markets`:
no Vietnamese source; the bot refuses US data for a Vietnamese stock (M2 design).

## Not done

- VPS install with the systemd unit (`docs/van-hanh-vps.md`): left to the owner.
- Second-account allowlist check on the live bot.
