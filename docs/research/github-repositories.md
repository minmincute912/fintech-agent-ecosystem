# Open-source project review (Phase 0, Task 3)

Scope: personal, long-only, end-of-day swing research on HOSE/HNX/UPCoM. Research only; nothing was cloned, installed or run. All metadata was read through web pages and `api.github.com` GET endpoints on 2026-10-27 (access date for every row below). Pages were read through a summarising fetch tool, so quotes are short and line numbers are approximate. Endpoint data terms are out of scope here (see the data-source document); this document covers software licences only.

"Last commit" below is the repo `pushed_at` timestamp unless a commit list was read. It can include non-default-branch pushes.

## vnstock: which repository is current

- `thinh-vu/vnstock` is the active repository: not archived, last push 2026-10-13, 1417 stars, homepage vnstocks.com. [Fact S1]
- Its README says the repo holds the **legacy 4.x code, "preserved for historical reference"**. Generation 5 is distributed as precompiled packages from vnstocks.com/download, not from this repo. [Fact S2]
- Latest GitHub release is v4.0.9, published 2026-09-27, with an empty body. [Fact S5]
- `vnstock-official/vnstock` is a 28-commit repository whose last commit is 2023-04-15 (last push 2023-05-14), 7 stars, no releases, MIT licence, copyright "2022 Thinh Vu". It targets TCBS and SSI sources. [Fact S8, S9, S10, S11]
- Relation between the two: the `vnstock-official` README links back to `thinh-vu/vnstock`, but no page states the relationship. The `thinh-vu` README never mentions `vnstock-official`. [Unverified → P1 check: confirm the relationship with the maintainer or vnstocks.com; treat `vnstock-official` as a stale 2023 snapshot until then]
- The MIT licence in `vnstock-official` is for that 2023 snapshot only. It does not carry over to Gen 4/5 code. [Assumption]

### vnstock licence terms (current)

- The repo's `LICENSE.md` is a **summary copy**, effective version `license-2026.09`; it says the website version governs. [Fact S3]
- The website text read on 2026-10-27 is `license-2026.11`, published 2026-10-24, **effective 2026-11-30, so not yet in force**. Two versions are therefore in play within five weeks. [Fact S4]
- Community edition: free for "personal, study and research use". It is source-available under Vnstock's own licence, not OSI-approved. [Fact S2, S3, S4]
- Extended editions (Bronze/Silver/Golden single user, Diamond a small group) may be used for the licensee's own work including investing and income-earning, within seat, device and quota limits. [Fact S4]
- Redistributing the software or activation keys, or building a product whose main value is giving third parties data access, needs a separate written agreement. Evading quota limits is prohibited. [Fact S3, S4]
- The licence says it "does not grant rights to third-party source data", that Vnstock is not a data provider, and that no tier carries a right to resell or redistribute source data. [Fact S3, S4]
- **Software licence is not a data licence.** Whether the endpoints behind vnstock (KBS, VCI, FMarket, MSN tags in the README) allow storage, automated access or model training is a separate question handled in the data-source document. [Fact S2]
- Owner's stated use (personal research) fits the Community edition on its face. Quota and device-registration mechanics, and whether the Community edition covers automated daily ingestion, are unknown. [Unverified → P1 check: read the full licence and quota table on vnstocks.com before any Phase 1 dependency decision]
- The reviewer's reading is not legal advice. The Vietnamese governing-law clause was not read. [Unverified → P1 check: read the Vietnamese original of the governing-law and termination clauses]
- Gen 5 is precompiled and obtained through vnstocks.com/download, so its code cannot be reviewed from GitHub, and download/activation may need an account (not permitted in Phase 0). [Fact S2] [Owner decision needed: whether to depend on a precompiled, account-gated client]
- A 2026-10-06 commit changed the default `user_agent` to a browser-like string "not carrying the project name". A 2026-09-26 commit added retry, circuit-breaker and block-detection utilities. [Fact S7] Interpretation: the library works around source-side blocking. That raises terms-of-service risk for automated access. [Assumption]

## Comparison

| Project | Repo URL | Latest release + date | Last commit | Licence | Vietnam compatibility | PIT support | Backtest assumptions | Tests/CI | Dependency footprint | Verdict (reuse/adapt/study/reject) | Reason |
|---|---|---|---|---|---|---|---|---|---|---|---|
| vnstock (thinh-vu) | https://github.com/thinh-vu/vnstock | v4.0.9, 2026-09-27 [Fact S5] | 2026-10-13 [Fact S1] | Custom source-available `license-2026.09` (website `2026.11` effective 2026-11-30); GitHub shows NOASSERTION [Fact S1, S3, S4] | Vietnam-only data client; tags KBS, VCI, FMarket, MSN [Fact S2] | None stated; client-side tool, not a data provider [Fact S2] | None (not a backtester); `vnstock_quant` add-on exists, not reviewed [Fact S2] | `tests/`, `pytest.ini`, `.github/` present; run status not read [Fact S2] | Not read | study | Candidate data client only. Licence is tiered and changing, Gen 5 is precompiled, and the data terms are separate. Not a backtester. |
| vnstock-official | https://github.com/vnstock-official/vnstock | none listed [Fact S9] | 2023-04-15 (last push 2023-05-14) [Fact S8, S11] | MIT, "Copyright (c) 2022 Thinh Vu" [Fact S10] | TCBS and SSI sources, Python 3.7+ [Fact S9] | None stated | None | No tests or CI seen in the file list [Fact S9] | Not read | reject | Stale 2023 snapshot; 7 stars; sources likely changed since. Relationship to thinh-vu unconfirmed. |
| Qlib | https://github.com/microsoft/qlib | v0.9.8, 2026-10-08 [Fact S14] | 2026-10-22 [Fact S12] | MIT [Fact S12] | None; docs show US and China (`--region cn`), Vietnam not mentioned. Official dataset temporarily disabled; README points to community Yahoo-derived data it says "might not be perfect" [Fact S13] | A point-in-time database is listed in the feature timeline (2022-03-10, PR #343) [Fact S13]; its fit to Vietnamese fundamentals is unverified [Unverified → P1 check: read Qlib PIT docs for storage format and announcement-date handling] | `Exchange` has `limit_threshold` (float, or per-row boolean expressions), `trade_unit` (docstring "100 for China A market"), `volume_threshold` (per-order-window expressions), `deal_price`, costs, suspension check [Fact S15]. **No T+N sell lock or holding-period tracking** [Fact S15]. | Test workflow runs pytest on 3 OS and Python 3.8-3.12 [Fact S16] | Large ML-oriented stack; exact list not read [Unverified → P1 check: read `setup.py`/`pyproject.toml`] | study | Closest conceptual match (limits, lot unit, volume cap, PIT). Settlement delay and exchange-specific, date-varying limits would need custom code; heavy and ML-centred. Study the PIT and Exchange design only. |
| vectorbt | https://github.com/polakowo/vectorbt | v1.2.0, 2026-10-19 [Fact S20] | 2026-10-23 [Fact S17] | Apache-2.0 with Commons Clause (no right to "Sell" the software); GitHub shows NOASSERTION [Fact S17, S18, S19] | None; generic market-agnostic | None | `from_orders`/`from_signals` document `size_granularity`, `max_size`, `min_size`, `allow_partial`, `lock_cash` (shorting only), `direction`. **No price-limit parameter, no volume/participation cap, no T+N lock** found in the first 100k of 248k characters of `portfolio/base.py` [Fact S21]; limit orders and leverage are PRO-only [Fact S19] | `tests/` and a `tests.yml` workflow exist; run status not read [Fact S19] | numba, pandas, numpy core; optional extras [Fact S19] | reject | Vectorised and fast but lacks settlement, limit-lock and participation-cap logic, and key features sit in the paid PRO edition. Commons Clause is acceptable for personal use but is a constraint if the platform is ever offered to others. |
| freqtrade | https://github.com/freqtrade/freqtrade | 2026.9, 2026-09-29 [Fact S24] | 2026-10-26 [Fact S22] | GPL-3.0 [Fact S22] | None; README scope is crypto exchanges (spot, futures) via CCXT [Fact S23] | None stated | Crypto backtesting, hyperopt, look-ahead and recursive-formula checks [Fact S23] | CI badge, codecov badge, `tests/` [Fact S23] | Python 3.12+, TA-Lib, Docker recommended [Fact S23] | reject | Crypto bot with execution tooling; no equity exchange rules; GPL-3.0 copyleft; it also targets live trading, which is out of scope. |
| lean-vn-quant | https://github.com/Vincent807759/lean-vn-quant | none [Fact S26] | 2026-10-27; repo created 2026-10-25, 25 commits, 3 stars [Fact S25, S26] | MIT [Fact S25] | Targets HOSE/VN30; Entrade (DNSE) OHLCV, inconsistently named in the README [Fact S26] | Universe mask uses lagged ADV; default basket is the 2026 VN30, which the README admits adds survivorship bias [Fact S26] | README claims: T+2.5 settlement ledger in `engine/vn_simulator.py`, +-7% limits with floor and ceiling lock, 100-share lots, volume-split fills with a 3% ADV20 cap, commission and sales tax [Fact S26]. The README does not state long-only. The code was not read [Unverified → P1 check: read `engine/vn_simulator.py` and verify each rule against the official rule text from Task 1] | An 8-stage `run_verification.py` and a CI workflow are named; no pass results shown [Fact S26] | numpy, polars, numba, scipy; pinned `requirements.txt` [Fact S26] | study | Most Vietnam-specific design found, but two days old, one author, and its headline returns are in-sample, on a survivorship-biased basket with private alphas excluded. Its ±7% limit is HOSE-only; HNX and UPCoM differ. Use as a checklist of ideas only; do not trust its numbers. |
| vnquant | https://github.com/phamdinhkhanh/vnquant | unknown | 2025-07-11 [Fact S27] | none listed [Fact S27] | Vietnam price scraper | None known | Not reviewed | Not reviewed | Not reviewed | reject | No licence means no right to reuse; README described as old and in development in search results (secondary) [Assumption]. |
| backtesting.py | https://github.com/kernc/backtesting.py | unknown [Unverified → P1 check: read releases page] | 2026-08-05 [Fact S28] | AGPL-3.0 [Fact S28] | Not assessed | Not assessed | Not assessed | Not assessed | Not assessed | reject | AGPL-3.0 copyleft; not assessed beyond licence. Reject on licence and scope grounds only. |
| zipline-reloaded | https://github.com/stefan-jansen/zipline-reloaded | 3.2.1, 2026-10-25 [Fact S30] | 2026-10-26 [Fact S29] | Apache-2.0 [Fact S29] | None; US equities heritage [Assumption] | Not assessed | `VolumeShareSlippage` caps fills at `volume_limit` 0.025 of bar volume and rejects fills worse than limit price. Whole shares only; **no round-lot logic** in `slippage.py` [Fact S31]. Calendar, T+N, price-limit handling not reviewed [Unverified → P1 check: read the trading calendar and order-blotter code] | Not assessed | Not assessed | study | Useful reference for a volume-share fill cap. Bundle ingestion and heavy event loop are likely overkill for EOD daily research [Assumption]. |

## Backtester fit against the five Vietnam constraints

| Constraint | Qlib | vectorbt | zipline-reloaded | lean-vn-quant (README only) |
|---|---|---|---|---|
| Price limits | Yes, config or expression; one rule set per run [Fact S15] | No parameter found [Fact S21] | Limit-price check on orders only, not market limits [Fact S31] | Claimed, +-7% [Fact S26] |
| Settlement delay before resale | No [Fact S15] | No [Fact S21] | Not reviewed | Claimed [Fact S26] |
| Lot size | `trade_unit` [Fact S15] | `size_granularity` [Fact S21] | None seen [Fact S31] | Claimed, 100 [Fact S26] |
| Long-only cash | Cash and position checks in order calculation [Fact S15] | `direction`, `lock_cash` [Fact S21] | Not reviewed | Not stated |
| Volume-capped fills | `volume_threshold` [Fact S15] | None found [Fact S21] | `volume_limit` 2.5% [Fact S31] | Claimed, 3% ADV20 [Fact S26] |

No reviewed project covers all five without custom code. Only Qlib and the unverified README claims of lean-vn-quant come close, and the settlement delay is missing from every verified source. [Assumption: based on the portions of source actually read]

## Recommendation

1. **Backtester: build a small purpose-built daily backtester** (spec §8 option). The deciding fact is that the settlement delay and exchange- and date-specific limit and lot rules are absent from every verified candidate, and these rules are the core of the Vietnam execution model. [Assumption] Library adaptation would mean forking or heavy patching of a large framework (Qlib) or one with feature gaps behind a paid edition (vectorbt PRO). A daily, long-only, cash-constrained loop is small, deterministic and testable. [Assumption] [Owner decision needed: confirm the build-versus-adapt choice, since it is architectural]
2. **Study, don't depend:** Qlib's `Exchange` parameters and point-in-time design, and zipline's volume-share fill cap, as design references. Re-implement; do not copy code.
3. **lean-vn-quant:** use only as an idea checklist; verify every rule it encodes against official sources (Task 1) before adopting any of it.
4. **vnstock:** a possible Phase 1 data client, not a foundation. Decide only after the data-terms document and a read of the full current licence and quota. [Owner decision needed]
5. **Reject:** vnstock-official (stale), vectorbt (gaps plus PRO split), freqtrade (crypto, GPL, live trading), vnquant (no licence), backtesting.py (AGPL).
6. No project here supplies adjusted-price, corporate-action or PIT fundamentals data for Vietnam. Data work stays with the data-source document. [Assumption: not verified beyond the READMEs read]

## Sources

All rows: publisher is the named GitHub repository owner unless noted. Access date 2026-10-27. Document date is shown only where the page gave one.

| ID | URL | Document date | Access date |
|---|---|---|---|
| S1 | https://api.github.com/repos/thinh-vu/vnstock | pushed_at 2026-10-13 | 2026-10-27 |
| S2 | https://github.com/thinh-vu/vnstock (README) | none shown | 2026-10-27 |
| S3 | https://github.com/thinh-vu/vnstock/blob/main/LICENSE.md (read via raw.githubusercontent.com) | version `license-2026.09` | 2026-10-27 |
| S4 | https://vnstocks.com/onboard/giay-phep-su-dung (Vnstock, vendor licence page, Vietnamese) | `license-2026.11`, published 2026-10-24, effective 2026-11-30 | 2026-10-27 |
| S5 | https://api.github.com/repos/thinh-vu/vnstock/releases/latest | 2026-09-27 | 2026-10-27 |
| S6 | https://github.com/thinh-vu/vnstock/releases (dates without year) | none | 2026-10-27 |
| S7 | https://api.github.com/repos/thinh-vu/vnstock/commits?per_page=3 | 2026-09-26 to 2026-10-13 | 2026-10-27 |
| S8 | https://api.github.com/repos/vnstock-official/vnstock | pushed_at 2023-05-14 | 2026-10-27 |
| S9 | https://github.com/vnstock-official/vnstock | none shown | 2026-10-27 |
| S10 | https://raw.githubusercontent.com/vnstock-official/vnstock/main/LICENSE | copyright 2022 | 2026-10-27 |
| S11 | https://api.github.com/repos/vnstock-official/vnstock/commits?per_page=2 | 2023-04-15 | 2026-10-27 |
| S12 | https://api.github.com/repos/microsoft/qlib | pushed_at 2026-10-22 | 2026-10-27 |
| S13 | https://github.com/microsoft/qlib (README) | none shown | 2026-10-27 |
| S14 | https://api.github.com/repos/microsoft/qlib/releases/latest | 2026-10-08 | 2026-10-27 |
| S15 | https://raw.githubusercontent.com/microsoft/qlib/main/qlib/backtest/exchange.py | none | 2026-10-27 |
| S16 | https://raw.githubusercontent.com/microsoft/qlib/main/.github/workflows/test_qlib_from_source.yml | none | 2026-10-27 |
| S17 | https://api.github.com/repos/polakowo/vectorbt | pushed_at 2026-10-23 | 2026-10-27 |
| S18 | https://raw.githubusercontent.com/polakowo/vectorbt/master/LICENSE.md | copyright 2026 | 2026-10-27 |
| S19 | https://github.com/polakowo/vectorbt (README) | none shown | 2026-10-27 |
| S20 | https://api.github.com/repos/polakowo/vectorbt/releases/latest | 2026-10-19 | 2026-10-27 |
| S21 | https://raw.githubusercontent.com/polakowo/vectorbt/master/vectorbt/portfolio/base.py (first 100k of 248k chars read) | none | 2026-10-27 |
| S22 | https://api.github.com/repos/freqtrade/freqtrade | pushed_at 2026-10-26 | 2026-10-27 |
| S23 | https://github.com/freqtrade/freqtrade (README) | none shown | 2026-10-27 |
| S24 | https://api.github.com/repos/freqtrade/freqtrade/releases/latest | 2026-09-29 | 2026-10-27 |
| S25 | https://api.github.com/repos/Vincent807759/lean-vn-quant | created 2026-10-25, pushed 2026-10-27 | 2026-10-27 |
| S26 | https://github.com/Vincent807759/lean-vn-quant (README) | none shown | 2026-10-27 |
| S27 | https://api.github.com/repos/phamdinhkhanh/vnquant | pushed_at 2025-07-11 | 2026-10-27 |
| S28 | https://api.github.com/repos/kernc/backtesting.py | pushed_at 2026-08-05 | 2026-10-27 |
| S29 | https://api.github.com/repos/stefan-jansen/zipline-reloaded | pushed_at 2026-10-26 | 2026-10-27 |
| S30 | https://api.github.com/repos/stefan-jansen/zipline-reloaded/releases/latest | 2026-10-25 | 2026-10-27 |
| S31 | https://raw.githubusercontent.com/stefan-jansen/zipline-reloaded/main/src/zipline/finance/slippage.py | none | 2026-10-27 |
