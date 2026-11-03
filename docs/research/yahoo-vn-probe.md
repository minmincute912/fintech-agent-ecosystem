# Yahoo Finance coverage of Vietnamese stocks (M1 Task 2 probe)

- Run: 2026-11-03T17:47+07:00, `uv run python -I scripts/probe_yahoo_vn.py`, yfinance 1.7.0
- Source label: **research-only** (see Yahoo terms below)
- Verdict: **gate failed** — no VN-Index history, and Yahoo's terms prohibit
  automated access without permission. M1 stopped at Task 2 Step 5 for an
  owner decision.

## Raw output (pandas deprecation warnings removed)

```
VNM.VN         rows= 520 first=2024-11-04 last=2026-11-03 last_close=56300.00 splits=0 dividends=4
FPT.VN         rows= 522 first=2024-11-04 last=2026-11-03 last_close=50400.00 splits=2 dividends=4
HPG.VN         rows= 522 first=2024-11-04 last=2026-11-03 last_close=21250.00 splits=2 dividends=1
SHS.VN         NO DATA (empty)
PVS.VN         NO DATA (empty)
ACV.VN         NO DATA (empty)
SHS.HN         NO DATA (empty)
^VNINDEX       NO DATA (empty)
^VNINDEX.VN    rows=   1 first=2026-11-03 last=2026-11-03 last_close=1699.62 splits=0 dividends=0
VNINDEX.VN     NO DATA (empty)
^VNI           NO DATA (empty)
```

Follow-up probe, same date:

```
^VNINDEX.VN period='max'                -> "Period 'max' is invalid, must be one of: 1d, 5d"; 0 rows
^VNINDEX.VN period='1y'                 -> 1 row (2026-11-03)
^VNINDEX.VN start=2026-09-01 end=11-04  -> 1 row (2026-11-03)
^VN30, VN30.VN                          -> 404 "Quote not found"
E1VFVN30.VN (VN30 ETF)                  -> 471 rows, 2025-01-13 .. 2026-11-03
FUEVFVND.VN (ETF)                       -> 496 rows, 2024-11-04 .. 2026-11-03
```

## Findings

| Item | Finding | Tag |
|---|---|---|
| Suffix | `.VN` works for the three probed tickers; `VN_SUFFIX = ".VN"` | Fact (probe) |
| Exchanges covered | VNM, FPT, HPG have data. SHS, PVS (believed HNX) and ACV (believed UPCoM) return nothing under `.VN` or `.HN`. | Fact (probe); exchange of each ticker **unverified** (hsx.vn / hnx.vn not checked) |
| History depth | About 2 years requested and returned for covered tickers; longer not probed | Fact (probe) |
| Units | Closes in VND (56300.00 for VNM), not thousands | Fact (probe) |
| Splits | FPT and HPG show 2 split rows each in 2 years (VN stock dividends appear as splits) | Fact (probe); adjustment method unverified |
| VN-Index | `^VNINDEX.VN` serves only 1d/5d periods: **no history**, so it cannot settle a 5-session holding period or backtest | Fact (probe) |
| Benchmark substitute | VN30 ETFs (E1VFVN30.VN, FUEVFVND.VN) have history; not chosen — plan forbids picking a substitute without the owner | Fact (probe) / Owner decision needed |

## Yahoo terms

Yahoo Terms of Service, https://legal.yahoo.com/us/en/yahoo/terms/otos/index.html,
accessed 2026-11-03 (page cites versions dated 15 May 2025 and 2 Jan 2026;
first 100,000 of ~127,000 characters read):

- §2(d)(9): you may not "access or collect data ... from our Services using any
  automated means, including but not limited to robots, spiders, scrapers, data
  mining tools ... for any purpose without our express, prior permission."
- §2(d)(10)(a): not "to create any database, archive, ... data feed".
- §2(e): no access or reuse "for any commercial purpose" unless expressly stated.

yfinance calls Yahoo programmatically, which is automated access. Under Owner
decision 1 (2026-10-27 spec §11) automated access must be permitted before a
source feeds the pipeline. **Yahoo fails that test.** It is usable at most as a
manual, research-only cross-check. The same applies to TradingAgents' default
Yahoo vendor for any market.
