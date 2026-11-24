# M2 measured runs and cost (Task 9)

Run 2026-11-25, 00:32–00:45 Asia/Ho_Chi_Minh. Command: `vsi analyze <T> --date 2026-11-23`.
2026-11-23 was the last DNSE daily bar at 00:30 on 2026-11-25 (no 2026-11-24 bar). Code at
commit `afef858` on branch `m2-vn-fundamentals-news` (before the billion-VND fix, see below),
TradingAgents 0.7.1, OpenAI, quick `gpt-6-luna`, deep `gpt-6-sol`, `max_tokens` 4096, output in
Vietnamese, analysts market + fundamentals + news.

## News collection before the runs

`uv run vsi collect-news`, 2026-11-25 ~00:20 (after the Tuổi Trẻ date fix): VnExpress 60,
VnEconomy 50 + 50, CafeF 50 + 50, Vietstock 20, Tuổi Trẻ 50 new items; both Báo Đầu tư feeds
returned a valid but empty channel (0 items). Store: 330 items, earliest published 2026-11-12.

## Runs (`~/.tradingagents/logs/vsi_runs.jsonl`, `report_path` omitted)

```
{"ticker": "VNM.VN", "date": "2026-11-23", "rating": "Hold", "llm_calls": 16, "tool_calls": 29, "tokens_in": 117829, "tokens_out": 19691, "seconds": 163.1, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
{"ticker": "VCB.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 16, "tool_calls": 25, "tokens_in": 119234, "tokens_out": 20400, "seconds": 142.8, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
{"ticker": "SHS.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 15, "tool_calls": 21, "tokens_in": 103529, "tokens_out": 20507, "seconds": 133.5, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
{"ticker": "ACV.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 16, "tool_calls": 26, "tokens_in": 98411, "tokens_out": 19852, "seconds": 156.5, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
```

`tool_calls` is now counted (it was 0 in M1).

## Cost per run

Prices as in `m1-run-cost.md` (read 2026-11-24): `gpt-6-luna` $0.10 in / $0.50 out,
`gpt-6-sol` $2.00 in / $10.00 out per 1M tokens. The log has totals, not tokens per model.

| Run | All at `gpt-6-luna` (floor) | All at `gpt-6-sol` (ceiling) |
|---|---|---|
| VNM | $0.022 | $0.433 |
| VCB | $0.022 | $0.442 |
| SHS | $0.021 | $0.412 |
| ACV | $0.020 | $0.395 |
| Four runs | $0.084 | $1.683 |

Fact: the four runs cost at most $1.68. Assumption: 2 of the ~16 calls are deep-tier (research
manager, portfolio manager) and carry most of the debate context, so about $0.10–0.20 per run.
The OpenAI dashboard (Usage, by model) gives the exact figure. Compared with M1 (market analyst
only, 45–65k input tokens), M2 uses about 1.6–2× the tokens and takes 2.2–2.7 minutes.

## Step 3 checks

| Check | Result |
|---|---|
| Fundamentals figures equal the tool output | VCB: NII 20,39 nghìn tỷ, +6,5% QoQ, +39,1% YoY; total operating income 25,43; provisions 6,18 (+697,3% YoY); NPAT 9,04 (−37,9% QoQ, +0,2% YoY) — all equal `get_fundamentals`. VNM: revenue 18,47 nghìn tỷ, gross profit 7,64, NPAT 2,96 — equal. ACV: total assets 96,60 nghìn tỷ, equity 76,34 — equal. SHS: total assets 29,05 nghìn tỷ, +43,3% YoY; NPAT 203,3 tỷ, −57,5% YoY — equal. **Fail on one figure:** SHS revenue written as "1.002 nghìn tỷ đồng" (1,002 nghìn tỷ in Vietnamese notation, 1000× too large; the source value is 1,001.99 tỷ). The same report also writes "1.002 tỷ đồng" correctly. |
| No news after D | No report cites a news date after 23/11/2026; reports cite outlets and dates, not links. **Pass.** |
| No FRED/Polymarket numbers | ACV's news report says the FRED requests returned DATA_UNAVAILABLE and that US data is not used; no US macro number appears in any report. **Pass.** |
| Agent arithmetic on statements | VCB: "provisions ≈ 35,5% of pre-provision profit", "12,3× Q2"; VNM: "selling expenses ≈ 21,0% of revenue". Spot-checked correct (6,184/17,402 = 35,5%; 3,885/18,465 = 21,0%), but these are LLM computations, not tested code. |

## Fix after the runs

The SHS unit error came from giving the agent raw VND (1,001,990,396,188) and letting it convert.
Commit `8b4b8f2` makes the tools print billion VND with 2 decimals (EPS stays VND per share), so
the agent quotes figures without converting. Re-run of SHS at commit `8b4b8f2`, 2026-11-25 00:47:

```
{"ticker": "SHS.VN", "date": "2026-11-23", "rating": "Underweight", "llm_calls": 16, "tool_calls": 25, "tokens_in": 118468, "tokens_out": 20922, "seconds": 151.3, "model_quick": "gpt-6-luna", "model_deep": "gpt-6-sol", "data_source": "DNSE OpenAPI"}
```

The report now writes revenue "1.001,99 tỷ đồng" and total assets "29.054 tỷ"; "nghìn tỷ" does
not appear. **Pass.** It still adds its own sums (short-term borrowings + bonds ≈ 15.935 tỷ,
1,27× equity), labelled as its own calculation. Cost bounds of this run: $0.022–0.446.

## Observations

- Company news is thin: in the 7 days to 23/11 the store matched VNM 1, VCB 2, SHS 0, ACV 0
  items. The RSS business feeds rarely name mid-caps; reports say so instead of inventing news.
- Market news includes general business items (gold, tourism, foreign tech) that the agents
  correctly treat as weak context.
- VCB: the bank summary was used as intended (NII, provisions, no "revenue"); the agent added
  ratios of its own (above). No notes-based metrics (NPL, CASA, CAR) were claimed.
