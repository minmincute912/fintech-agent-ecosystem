# M1 measured runs and cost (Task 9)

Run 2026-11-24, about 18:17–18:23 Asia/Ho_Chi_Minh. Command: `vsi analyze <T> --date 2026-11-23`.
2026-11-23 was the last DNSE daily bar at 18:15 that day (the 2026-11-24 bar was not yet
published). Code at commit 96b9e29, TradingAgents 0.7.1, OpenAI provider, quick `gpt-6-luna`,
deep `gpt-6-sol`, `max_tokens` 4096, output language Vietnamese, market analyst only.

## Runs (`~/.tradingagents/logs/vsi_runs.jsonl`)

```
{"ticker": "VNM.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 12, "tool_calls": 0, "tokens_in": 64851, "tokens_out": 10396, "seconds": 99.9, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
{"ticker": "SHS.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 11, "tool_calls": 0, "tokens_in": 44886, "tokens_out": 11508, "seconds": 135.6, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
{"ticker": "ZZZ.VN", "date": "2026-11-23", "rating": "Hold", "llm_calls": 11, "tool_calls": 0, "tokens_in": 23612, "tokens_out": 7624, "seconds": 88.7, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
```
(`report_path` fields omitted.)

## Prices

OpenAI standard prices per 1M tokens, short context, read 2026-11-24 from
https://developers.openai.com/api/docs/pricing: `gpt-6-luna` $0.10 input, $0.01 cached input,
$0.50 output; `gpt-6-sol` $2.00 input, $0.20 cached input, $10.00 output.

## Cost per run

The usage log records total tokens, not tokens per model, so exact cost needs the OpenAI
dashboard (Usage, by model). Bounds from the logged totals, ignoring cache discounts:

| Run | All tokens at `gpt-6-luna` (floor) | All tokens at `gpt-6-sol` (ceiling) |
|---|---|---|
| VNM | $0.012 | $0.234 |
| SHS | $0.010 | $0.205 |
| ZZZ | $0.006 | $0.123 |
| Three runs | $0.028 | $0.562 |

Fact: the three runs together cost at most $0.56. Most calls (about 9 of 11–12) go to the
quick tier; the deep tier handles the research manager and portfolio manager, so the real cost
sits well below the ceiling. Assumption: about $0.05–0.10 per run with real data.

## Step 3 checks

| Check | Result |
|---|---|
| Cited close equals DNSE close for 2026-11-23 | VNM report cites close 52,30 (DNSE 52.3), with open 51,40, high 52,50, low 51,10, volume 2.126.000. SHS report cites close 13,40 six times (DNSE 13.4). **Pass.** |
| `ZZZ` reports data as unavailable, with no price | Market analyst: "Dữ liệu giá OHLCV không truy xuất được"; proposal "NO TRADE — wait for valid market data"; no decimal price appears anywhere in the report. Final rating is still **Hold**, labelled insufficient data. **Pass, with a note** below. |
| No Yahoo call | The word "yahoo" appears 0 times in the three run logs and the three reports. **Pass.** |

## Observations

- **Vietnamese:** the reports read as natural Vietnamese with Vietnamese number formatting
  (comma decimals, dot thousands). The final proposal line stays in English
  ("FINAL TRANSACTION PROPOSAL: WAIT …") because TradingAgents parses it.
- **Ungrounded claims:** with only the market analyst, the bull researcher argues from brand
  and business knowledge in the model, not from data. It does say so ("lần cung cấp này không có
  báo cáo tài chính …"). M2 fundamentals and news are needed before such claims carry evidence.
- **Unknown ticker still costs a full run** (11 LLM calls) and ends in a "Hold". A cheap guard
  would check `DnseClient.instrument()` before building the graph and refuse the run.
- **`tool_calls` is 0** in every run although the market report quotes indicator values from
  tools. The counter from `cli.stats_handler` seems not to see tool calls on this path
  (unverified); token and LLM-call counts are unaffected.
- **Duration:** 89–136 seconds per run.

## Projection (Assumption)

M2 adds the fundamentals and news analysts: two more analysts on the quick tier plus longer
debate context. A rough guess is 1.5–2× today's tokens, so about $0.10–0.20 per run. Measure
again in M2.
