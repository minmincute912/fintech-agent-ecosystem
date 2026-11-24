# VNDirect finfo probe and createdDate gate (M2 Task 6)

Run 2026-11-25 Asia/Ho_Chi_Minh with `uv run python -I scripts/probe_finfo.py --items`, code on
branch `m2-vn-fundamentals-news`. Source is research-only, personal use (owner decision
2026-11-24). Item lists for the four layouts (model type, item code, display order, latest
quarter value, Vietnamese | English name) are in `finfo-items.txt`.

## Access note

finfo answers HTTP 403 to Python's default `User-Agent` (`python-requests/…`,
`python-urllib/…`) and to an empty one, and 200 to `curl/8` and to an honest custom agent
`vsi-research/0.1 (personal research)`, checked with curl 2026-11-25. The client sends that
custom agent; it does not pretend to be a browser. The block may be aimed at scripts, so the
owner should know this source can be closed to us at any time.

## Raw output (dates per quarter, last 6 quarters; annual last 3)

```

VNM layout=corporate models=(1, 2, 3) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-30  2026-10-30   2026-10-30   209
2026-06-30   2026-07-30  2026-07-30   2026-08-17   209
2026-03-31   2026-05-04  2026-05-04   2026-05-18   209
2025-12-31   2026-01-30  2026-01-30   2026-03-02   189
2025-09-30   2025-10-30  2025-10-30   2025-10-31   189
2025-06-30   2025-07-30  2025-07-30   2025-07-31   189
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-31  2025-06-16
2024-12-31   2025-01-24  2025-06-16
2025-12-31   2026-01-30  2026-03-02

FPT layout=corporate models=(1, 2, 3) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-29  2026-10-29   2026-10-29   209
2026-06-30   2026-07-28  2026-07-28   2026-08-24   209
2026-03-31   2026-04-28  2026-04-28   2026-06-01   209
2025-12-31   2026-01-27  2026-01-27   2026-03-20   189
2025-09-30   2025-10-24  2025-10-24   2025-10-24   189
2025-06-30   2025-07-22  2025-07-22   2025-08-21   189
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-25  2024-03-11
2024-12-31   2025-01-24  2026-03-20
2025-12-31   2026-01-27  2026-03-20

HPG layout=corporate models=(1, 2, 3) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-29  2026-10-29   2026-10-29   209
2026-06-30   2026-07-30  2026-07-30   2026-09-04   209
2026-03-31   2026-05-04  2026-05-04   2026-05-18   209
2025-12-31   2026-01-30  2026-01-30   2026-05-18   208
2025-09-30   2025-10-29  2025-10-29   2025-10-29   189
2025-06-30   2025-07-18  2025-07-30   2025-09-03   189
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-30  2026-08-17
2024-12-31   2025-01-26  2026-08-17
2025-12-31   2026-01-30  2026-04-01

VCB layout=bank models=(101, 102, 103) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-30  2026-10-30   2026-10-30   178
2026-06-30   2026-07-30  2026-07-30   2026-08-19   178
2026-03-31   2026-04-29  2026-04-29   2026-04-29   178
2025-12-31   2026-01-30  2026-01-30   2026-11-18   178
2025-09-30   2025-10-30  2025-10-30   2025-10-30   178
2025-06-30   2025-07-30  2025-07-30   2025-08-13   178
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-31  2025-11-04
2024-12-31   2025-01-24  2026-10-29
2025-12-31   2026-01-30  2026-11-18

ACB layout=bank models=(101, 102, 103) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-28  2026-10-28   2026-10-28   178
2026-06-30   2026-07-22  2026-07-22   2026-08-19   178
2026-03-31   2026-04-23  2026-04-23   2026-04-23   178
2025-12-31   2026-01-28  2026-01-28   2026-02-27   178
2025-09-30   2025-10-22  2025-10-22   2025-10-22   178
2025-06-30   2025-07-24  2025-07-25   2025-08-15   178
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-27  2025-03-05
2024-12-31   2025-01-22  2025-03-05
2025-12-31   2026-01-28  2026-02-27

SSI layout=securities models=(89, 90, 91) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-30  2026-10-30   2026-10-30   408
2026-06-30   2026-07-31  2026-07-31   2026-08-19   408
2026-03-31   2026-04-23  2026-04-23   2026-04-23   408
2025-12-31   2026-01-22  2026-01-31   2026-03-30   408
2025-09-30   2025-10-27  2025-10-27   2026-02-02   408
2025-06-30   2025-07-31  2025-07-31   2026-08-19   408
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-31  2026-02-02
2024-12-31   2025-01-24  2026-03-30
2025-12-31   2026-01-22  2026-03-30

SHS layout=securities models=(89, 90, 91) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-21  2026-10-21   2026-10-21   408
2026-06-30   2026-07-21  2026-07-21   2026-08-14   408
2026-03-31   2026-04-21  2026-04-21   2026-04-21   408
2025-12-31   2026-01-20  2026-01-20   2026-03-24   408
2025-09-30   2025-10-15  2025-10-15   2025-10-15   408
2025-06-30   2025-07-18  2025-07-18   2025-10-15   408
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-22  2024-04-01
2024-12-31   2025-01-20  2025-03-07
2025-12-31   2026-01-20  2026-03-24

BVH layout=insurance models=(411, 412, 413) quarter rows=10000
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-10-30  2026-10-30   2026-11-02   303
2026-06-30   2026-07-31  2026-07-31   2026-09-03   303
2026-03-31   2026-04-29  2026-04-29   2026-05-18   303
2025-12-31   2026-02-02  2026-02-02   2026-05-18   303
2025-09-30   2025-10-30  2025-10-30   2025-11-18   303
2025-06-30   2025-07-31  2025-07-31   2025-11-03   303
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-31  2025-04-01
2024-12-31   2025-02-03  2026-05-18
2025-12-31   2026-02-02  2026-05-18

ACV layout=corporate models=(1, 2, 3) quarter rows=8307
            created_min created_max modified_max  rows
fiscal_date                                           
2026-09-30   2026-11-02  2026-11-02   2026-11-02   209
2026-06-30   2026-07-30  2026-07-30   2026-09-03   209
2026-03-31   2026-05-04  2026-05-04   2026-05-04   209
2025-12-31   2026-02-04  2026-02-04   2026-04-01   189
2025-09-30   2025-10-30  2025-10-30   2025-10-30   189
2025-06-30   2025-07-31  2025-07-31   2025-09-04   189
annual:
                created    modified
fiscal_date                        
2023-12-31   2024-01-31  2024-12-03
2024-12-31   2025-01-24  2025-04-01
2025-12-31   2026-02-04  2026-04-01
```

`created` is a date with time 00:00:00. Each `rows` value is the number of items in that period.
Quarterly values are per quarter, not year-to-date (VNM cash at start of Q3 2026 equals cash at
end of Q2 2026: 4,535,672,366,831).

## createdDate against publication (Q3 2026)

Publication evidence is the earliest dated news article found by web search on 2026-11-25
(`article:published_time` read from the page). Article time is an upper bound on publication.

| Ticker | finfo created | Earliest evidence of publication | Lag created − evidence | Figures cross-checked (finfo = article) |
|---|---|---|---|---|
| SHS | 2026-10-21 | mekongasean.vn 2026-10-21 09:15 | 0 days | revenue 1,001.99 bn = "gần 1.002 tỷ"; pretax 250.81 bn = 250,8; loan income 341.15 bn = 341,1; total assets 29,053.8 bn = 29.053 |
| ACB | 2026-10-28 | cafef.vn "sáng ngày 28/10", article id 2026-10-28 00:05 | 0 days | pretax 5,879.36 bn = 5.879,4; NPAT 4,698.84 bn = 4.698,8; credit provisions 933.83 bn = 933,8 |
| BVH | 2026-10-30 | anninhthudo.vn: results published 30/10/2026 | 0 days | Q3 NPAT 834.84 bn = 834,8 (vietbao.vn) |
| ACV | 2026-11-02 | doanhnhan.baophapluat.vn 2026-11-01 20:10 | +1 day | — |
| FPT | 2026-10-29 | cafef.vn 2026-10-21 08:38: FPT's own 9-month results release, before its statements | +8 days after the results release | — |
| VNM | 2026-10-30 | doanhnhan.baophapluat.vn 2026-10-31 14:41 (earliest found) | **−1 day** | net sales 18,465.19 bn = 18.465; parent NPAT 2,964.17 bn = 2.964 |

Findings:

- `created` differs by ticker (2026-10-21 to 2026-11-02), so it is not a single batch-load date
  as the 2026-11-24 note suspected. It sits on or a day after the first press report in four of
  six samples.
- **VNM is unconfirmed:** `created` is one day before the earliest article found. 2026-10-30 was
  the legal deadline for consolidated Q3 statements, so publication on the evening of 30/10 is
  likely but not shown. Owner check: the publication date of VNM's Q3 2026 statements on
  vinamilk.com.vn or HOSE.
- FPT announces results before its statements; `created` follows the statements, not the
  press release. No look-ahead in that direction.
- `created` is a date without a time. A statement published in the evening of day D counts as
  available on D; an analysis dated D can then see figures released after that day's close.
- Not checked: the three earlier quarters per ticker (5 × 4 samples in the plan). Only Q3 2026
  was compared.

## Restatements (`modified` > `created`)

Last 4 quarters × 9 tickers = 36 samples; 23 (64%) were modified after creation:
Q3 2026 1/9 (BVH, +3 days), Q2 2026 9/9 (modified in August, when reviewed half-year statements
come out), Q1 2026 4/9, Q4 2025 9/9 (modified in February–May, when audited annual statements
come out). finfo keeps only current values, so an analysis dated before a revision sees the
revised numbers. The tables mark such periods "(revised after analysis date)".

## Gate

| Condition (spec) | Result |
|---|---|
| `created` earlier than publication for any sample | Not shown for 5 of 6; VNM unconfirmed (−1 day against press, deadline-day publication likely) |
| Most lags over ~10 days | No: 0–1 day against press, 8 days only against FPT's pre-statement release |
| Most samples modified after creation | **Yes, 64%** |

Ruling (builder, 2026-11-25, owner may override): continue. The owner runs analyses on demand
for the latest session, where a revision after the analysis date cannot have happened yet; for
past dates the revised periods are labelled. M4 (historical evaluation) must treat labelled
periods as possibly contaminated.
