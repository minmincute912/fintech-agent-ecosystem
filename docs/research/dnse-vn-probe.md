# DNSE OpenAPI probe of Vietnamese stocks (M1 Task 8)

Run 2026-11-24 at about 16:03 Asia/Ho_Chi_Minh (09:03 UTC) with the owner's DNSE keys,
`uv run python -I scripts/probe_dnse_vn.py`, `vsi/dnse.py` at commit ac03f06.
No keys or signatures were printed.

## Raw output

```
run 2026-11-24, window 2021-11-25..2026-11-24
VNM   {'name': 'CTCP Sữa Việt Nam', 'market': 'HOSE'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=52.3 max_abs_daily_move=6.96% on 2026-01-14
FPT   {'name': 'CTCP FPT', 'market': 'HOSE'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=46.85 max_abs_daily_move=7.00% on 2025-04-16
HPG   {'name': 'CTCP Tập đoàn Hòa Phát', 'market': 'HOSE'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=20.4 max_abs_daily_move=7.02% on 2022-12-06
SHS   {'name': 'CTCP Chứng khoán Sài Gòn - Hà Nội', 'market': 'HNX'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=13.4 max_abs_daily_move=10.07% on 2022-11-25
PVS   {'name': 'Tổng CTCP Dịch vụ Kỹ thuật Dầu khí Việt Nam', 'market': 'HNX'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=26.9 max_abs_daily_move=10.03% on 2022-05-12
ACV   {'name': 'Tổng Công ty Cảng Hàng không Việt Nam - CTCP', 'market': 'UPCOM'} rows=1244 first=2021-11-25 last=2026-11-23 last_close=37.0 max_abs_daily_move=13.19% on 2025-04-03
ZZZ   NO DATA (DNSE /price/ohlc failed: HTTP 400 BAD_REQUEST invalid symbol)
VNINDEX rows=1242 first=2021-11-25 last=2026-11-23 last=1697.14
```

Follow-up check, same day: closes since 2025-05-05 that are not on the HOSE tick grid
(quant-methodology.md "Tick size", HOSE: <10,000 = 10 VND; 10,000–49,950 = 50; ≥50,000 = 100).

```
VNM rows 391 off-tick closes 350 last off-tick date 2026-11-09
FPT rows 391 off-tick closes 313 last off-tick date 2026-09-18
HPG rows 391 off-tick closes 192 last off-tick date 2026-05-21
```

## Findings

| Question | Answer | Label |
|---|---|---|
| Auth | Signed requests with the `Date` header are accepted; `X-Aux-Date` not needed. | Fact (probe) |
| Coverage | HOSE (VNM, FPT, HPG), HNX (SHS, PVS) and UPCoM (ACV) all return 5 years of daily bars; exchange per `/market/instruments`. | Fact (probe) |
| VNINDEX | `type=INDEX`, symbol `VNINDEX`: 1,242 rows in 5 years (about 248 a year). Code matches `VN_BENCHMARK`. | Fact (probe) |
| Unknown ticker | HTTP 400 `BAD_REQUEST invalid symbol`. The client raises `VendorUnavailableError`, so the router reports `DATA_UNAVAILABLE`, not a price. A `NO_DATA_AVAILABLE` label would be more precise. | Fact (probe) |
| Price unit | Thousand VND (VNM 52.3 = 52,300 VND). | Assumption (spec example + price level; not cross-checked with an exchange page) |
| Unfinished session | At 16:03 on 2026-11-24 (a Tuesday, after the close) the last bar was 2026-11-23, so the day's bar was not yet published. Behaviour during trading hours not observed. | Fact (probe) / unknown |
| Corporate-action adjustment | History is adjusted backward. Older closes fall off the tick grid, and recent ones are on it. The cut-over date differs per ticker (VNM 2026-11-09, FPT 2026-09-18, HPG 2026-05-21), which fits re-adjustment at each ex-date. HPG's first close is 25.2 on 2021-11-25. Largest daily moves stay within the HOSE ±7%, HNX ±10% and UPCoM ±15% bands, so no unadjusted ex-date gap is visible. | Assumption (inferred; no DNSE statement, no event dates checked) |

## Gate (plan Task 8 Step 5)

- VNINDEX ≥ 200 rows a year: **pass** (about 248).
- At least one HOSE ticker returns data: **pass**.
- Adjustment for corporate actions determined: **pass, by inference** (above). Consequence: past
  values change after each new corporate action, so a re-run for an old date can see slightly
  different prices than the first run did.

Task 9 can run once the owner adds `OPENAI_API_KEY` and approves three paid runs.

## Notes for a daily schedule (not M1 scope)

The day's bar was missing at 16:03, so a scheduled run must start later, or check that the
last bar's date equals the analysis date before spending LLM credit. When DNSE publishes the
bar is unknown.
