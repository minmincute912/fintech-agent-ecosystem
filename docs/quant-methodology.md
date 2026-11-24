# Quantitative Methodology

Status: Phase 0 draft. Access date for all sources: 2026-10-27. Research and decision support only; no brokerage execution.

Tags: `[Fact Sn]` = stated by source `Sn`; `[Assumption]`; `[Owner decision needed]`; `[Unverified → P1 check: ...]`. Vietnamese originals are cited and paraphrased in English. Exchange abbreviations: HOSE = HoSE (Ho Chi Minh City Stock Exchange), HNX = Hanoi Stock Exchange (listed board), UPCoM = HNX's unlisted-public-company market.

## Market rules

Rule values are "as of 2026-10-27". Where an earlier value is known, the "Changes in last 10 years" column gives it with the change date, because a backtest needs the rule as of each date. Window = 2016-10-27 to 2026-10-27. Row names are stable and are cited by later sections.

Reading notes:
- The HOSE rows rest mainly on S1 (HOSE's own investor guide, issued under Decision 22/QĐ-HĐTV dated 18/04/2025, which took effect when the new KRX-based system went live on 2025-05-05). HNX rows rest on S2 (the text of the same Decision) and S4. UPCoM rows rest on S5, a broker summary, so are weaker.
- hnx.vn failed TLS certificate verification, so no HNX primary page was read directly. See Unverified items.
- Prices are in VND. "Lot" = trading unit for matching.

Notes:
- N1: Rows tagged "(see N1)" read Decision 22/QĐ-HĐTV through a legal-text mirror (S2), which itself lists a later 2026 22/QĐ-HĐTV that replaces the 2025 text. [Unverified → P1 check: obtain the official 2026 and 2025 texts from HOSE/HNX/VNX and diff them against every S2-based row]
- N2: UPCoM values rest on one broker summary (S5), so they are tagged Assumption or Unverified until HNX's UPCoM trading regulation is read.

### Trading mechanics

| Rule | Exchange | Current value | Effective since | Changes in last 10 years | Tag/Source |
|---|---|---|---|---|---|
| Trading days | All | Monday to Friday, excluding public holidays under the Labour Code (SGDCK tổ chức giao dịch "từ thứ Hai đến thứ Sáu hàng tuần"). | KRX-era Decision 22/QĐ-HĐTV, 2025-05-05 (text itself says Mon-Fri; earlier text not read). | No Saturday or Sunday trading is stated in any source read. Earlier-text check not done: [Unverified → P1 check: confirm Mon-Fri in the 2016-2025 rule texts (Decision 17/QĐ-HĐTV of 31/03/2022 and predecessors)]. | [Fact S2] (see N1) |
| Trading sessions | HOSE | Opening call auction (ATO) 09:00-09:15; continuous I 09:15-11:30; lunch break 11:30-13:00; continuous II 13:00-14:30; closing call auction (ATC) 14:30-14:45. Put-through 09:00-11:30 and 13:00-15:00. No order edits/cancels during the break. | 2025-05-05 (KRX go-live). | Session times before 2025-05-05 not read. HOSE Decision 894/QĐ-SGDHCM of 30/12/2020 is reported by a broker (BSC) to have amended trading units, trading times, bands and order types, effective 2021-01-04. [Unverified → P1 check: obtain Decision 894/QĐ-SGDHCM (2020-12-30) and Decision 352/QĐ-SGDHCM (2021) text and record session times for 2016-2025]. | [Fact S1] |
| Trading sessions | HNX | Continuous I 09:00-11:30; continuous II 13:00-14:30; closing call auction 14:30-14:45; after-hours periodic 14:45-14:55 and after-hours continuous 14:55-15:00 (round lots). Put-through 09:00-11:30, 13:00-14:45, plus after-hours. No opening auction. | 2025-05-05 (Decision 22/QĐ-HĐTV effective date). | Earlier times not read. S4 (broker summary) shows continuous I starting 09:15, which conflicts with S2. [Unverified → P1 check: confirm HNX continuous-session start time (09:00 per S2 vs 09:15 per S4) on hnx.vn] | [Fact S2] (see N1) |
| Trading sessions | UPCoM | CONFLICT: S5 gives continuous I 09:15-11:30 and continuous II 13:00-14:30; search snippets of an HNX decision effective 2017-06-20 (not read directly) give 09:00-11:30 and 13:00-15:00. Put-through 09:00-11:30 and 13:00-15:00 (S5). No call auctions. | Broker summary dated 2025-07-22. | Earlier times not read. [Unverified → P1 check: confirm UPCoM session times and whether continuous trading starts 09:00 or 09:15 from HNX's UPCoM trading regulation] | [Unverified → P1 check: UPCoM continuous-session times conflict (S5 vs snippets); obtain HNX UPCoM trading regulation] |
| Order types | HOSE | LO (limit), ATO, ATC, MTL (market-to-limit; unfilled remainder becomes a limit order one tick beyond the last price). MTL only in continuous sessions. | MTL and the ATO/ATC changes below: 2025-05-05. | At KRX go-live: the market-price (MP) order was replaced by MTL; ATO/ATC orders stopped having priority over limit orders already on the book and are shown at a price level; price and quantity can no longer be changed in one edit. Edit that only reduces quantity keeps queue priority. Before 2025-05-05, ATO/ATC had priority over limit orders in periodic matching. Order-type set before 2021 not read. | [Fact S1] (current set); [Assumption] (KRX change history, S6 news) |
| Order types | HNX | LO, MTL, MOK (fill-or-kill), MAK (match-and-cancel), ATC, PLO (after-hours limit). No ATO. | Broker summary dated 2025-07-22. | Earlier order types not read. [Unverified → P1 check: HNX order-type history 2016-2025] | [Fact S4] |
| Order types | UPCoM | LO only (plus put-through orders and advertisements). | Broker summary dated 2025-07-22. | Earlier set not read. [Unverified → P1 check: UPCoM order-type history 2016-2025] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Daily price limit | HOSE | ±7% of reference price for shares, closed-end funds, ETFs. Ceiling = reference + (reference × band); floor = reference - (reference × band). | Current as of S1 (Decision 22/QĐ-HĐTV, 2025-05-05). | Band history not pinned. A third-party legal-advice site and broker materials show 7% as long-standing, but no dated source. [Unverified → P1 check: confirm ±7% applied on HOSE throughout 2016-10 to 2025-05 from Decision 352/QĐ-SGDHCM and predecessors] | [Fact S1] |
| Daily price limit | HNX | ±10% of reference price for shares and ETFs. | Decision 22/QĐ-HĐTV, 2025-05-05 (Annex III). | Not pinned. [Unverified → P1 check: confirm ±10% throughout 2016-10 to 2025-05 from HNX trading regulation] | [Fact S2] (see N1) |
| Daily price limit | UPCoM | ±15% of reference price for shares. | Broker summary dated 2025-07-22. | Not pinned. News (S20) reports an HNX decision effective 2017-06-20 set the ±15% band and replaced Decision 79/QĐ-SGDHN of 2016-02-05, whose band is unknown [Assumption]. A broker-education page states UPCoM was raised from 10% to 15% on 2015-07-01 (outside the window), but no dated source. [Unverified → P1 check: confirm ±15% throughout 2016-10 to 2025-05 and the 2015 change from HNX's UPCoM trading regulation] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Price limit, first day / resumed trading | HOSE | ±20% on the first trading day of a new listing, and on resumption after suspension or halt of 25 or more consecutive trading days. Same ±20% on the ex-rights day for a spin-off of a listed company, treasury-share dividends or bonus shares, and cash dividends at or above the prior close (S3). | S1 (Decision 22/QĐ-HĐTV, 2025-05-05). | Earlier values not read. [Unverified → P1 check: obtain first-day band history from Decision 352/QĐ-SGDHCM (2021) and earlier HOSE rules] | [Fact S1] |
| Price limit, first day / resumed trading | HNX | ±30% on a newly listed share's first day (S2) and on resumption after 25+ sessions' suspension, and on ex-rights days for the same event types (S4). Securities newly listed or resumed after 25+ sessions: no put-through until a price is set by round-lot continuous matching (S4). | Decision 22/QĐ-HĐTV, 2025-05-05. | Earlier values not read. [Unverified → P1 check: first-day band history for HNX 2016-2025] | [Fact S2] (see N1) |
| Price limit, first day / resumed trading | UPCoM | ±40% on first trading day or resumption after 25+ sessions, until a reference price is set from round-lot continuous matching; same ±40% on ex-rights days for the event types in S5. No put-through or odd-lot trading on that day. | Broker summary dated 2025-07-22. | Earlier values not read. [Unverified → P1 check: first-day band history for UPCoM 2016-2025] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Tick size | HOSE | Shares and closed-end funds, continuous/periodic matching: price below 10,000 = 10 VND; 10,000-49,950 = 50 VND; 50,000 and above = 100 VND. ETFs and covered warrants: 10 VND at all prices. Put-through: 1 VND. | S1 (2025-05-05). | Tick schedule before 2025-05-05 not read. [Unverified → P1 check: obtain HOSE tick-size schedule by date for 2016-10 to 2025-05; the price grid affects backtest limit-price rounding] | [Fact S1] |
| Tick size | HNX | Shares: 100 VND for matching, 1 VND for put-through. ETFs: 1 VND. | S2 (Annex III, 2025-05-05). | Earlier values not read. [Unverified → P1 check: HNX tick history 2016-2025] | [Fact S2] (see N1) |
| Tick size | UPCoM | Shares: 100 VND for matching, 1 VND for put-through. | Broker summary dated 2025-07-22. | Earlier values not read. [Unverified → P1 check: UPCoM tick history 2016-2025] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Lot size | HOSE | Round lot 100 shares; maximum 500,000 per order. Large lot ("lô lớn", put-through): minimum 20,000. | 2021-01-04. | Was 10 shares until 2020-12-31 (500,000 per-order cap unchanged); changed to 100 on 2021-01-04. Whether 10 applied for all of 2016-10 to 2020-12 is not confirmed. S9 is a news report; the decision number (894/QĐ-SGDHCM) is from a broker note only. [Unverified → P1 check: obtain Decision 894/QĐ-SGDHCM and confirm no other lot-size change in 2016-2020] | [Fact S1] (current); [Assumption] (2021-01-04 date and prior lot of 10, S9 news; decision number from a broker note) |
| Lot size | HNX | Round lot 100 for matching; put-through minimum 5,000. | Decision 22/QĐ-HĐTV, 2025-05-05. | History not read. [Unverified → P1 check: HNX lot-size history 2016-2025] | [Fact S2] (see N1) |
| Lot size | UPCoM | Round lot 100 for matching; put-through minimum 5,000. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: UPCoM lot-size history 2016-2025] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Odd-lot trading | HOSE | 1-99 shares, limit orders only; same sessions as round lots. | KRX go-live 2025-05-05. | Before KRX, odd lots traded only in continuous matching and put-through; periodic-matching odd lots were added at KRX. Odd-lot prices are not used to set reference price or index. | [Fact S1] (current sessions and unit); [Assumption] (pre-KRX history, S6/S7 news) |
| Odd-lot trading | HNX | 1 share unit; limit orders only; odd-lot prices do not set reference price. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: odd-lot rules 2016-2025] | [Fact S4] |
| Odd-lot trading | UPCoM | 1 share unit; limit orders only; odd-lot prices do not set reference price. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: odd-lot rules 2016-2025] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Reference price | HOSE | Prior session's closing price, adjusted on ex-rights or ex-dividend day for the rights or dividend value (with exceptions for issues priced at or above the prior close, cash dividends at or above the prior close, and treasury-share stock dividends). Closing price = the ATC match. | S2, Art. 31(4)-(6) (2025-05-05). | Pre-KRX details not read. [Unverified → P1 check: ex-date reference-price formulae in Art. 31 and pre-2025 rules] | [Fact S2] (see N1) |
| Reference price | HNX | Prior session's closing price (adjusted on ex-date per S2 Art. 31). | 2025-05-05. | History not read. [Unverified → P1 check: HNX reference-price history 2016-2025] | [Fact S4] |
| Reference price | UPCoM | Volume-weighted average of round-lot continuous-matching prices on the prior day that had such trades (not the closing price). | Broker summary dated 2025-07-22. | History not read. Another source describes it as a simple average; [Unverified → P1 check: confirm UPCoM reference-price formula and any change dates in HNX's UPCoM regulation] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Put-through | HOSE | Negotiated trades via members, 09:00-11:30 and 13:00-15:00. Both sides can enter orders and the counterparty confirms. Executed deals cannot be edited or cancelled. | KRX go-live 2025-05-05. | Before KRX, an investor could cancel and re-enter a wrongly entered deal. | [Fact S1] (sessions; executed deals not editable); [Assumption] (pre-KRX history and two-sided entry, S6/S7 news) |
| Put-through | HNX | 09:00-11:30 and 13:00-14:45, plus after-hours; executed deals cannot be edited or cancelled; minimum 5,000 shares. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: HNX put-through history] | [Fact S4] |
| Put-through | UPCoM | 09:00-11:30 and 13:00-15:00; minimum 5,000 shares; not allowed on first day or on the first day after a 25+ session halt. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: UPCoM put-through history] | [Assumption] (S5 broker summary only; UPCoM regulation not read, see N2) |
| Restricted-status trading | HOSE | Securities under trading restriction (status RES) trade only by periodic matching: ATO, then fifteen 15-minute periodic auctions, then ATC; limit orders only except ATO/ATC; no edit/cancel in the last 5 minutes of each auction; round lots only. | KRX go-live 2025-05-05. | Before KRX, restricted stocks traded only in the afternoon. | [Fact S1] (current); [Assumption] (pre-KRX afternoon-only, S7 news) |
| Restricted-status trading | HNX | Restricted securities may trade on Fridays that are working days. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: HNX restricted-security trading schedule and history] | [Fact S4] |
| Restricted-status trading | UPCoM | Restricted securities may trade on Fridays that are working days. | Broker summary dated 2025-07-22. | History not read. [Unverified → P1 check: UPCoM restricted-security schedule and history] | [Assumption] (S5 broker summary only, see N2) |

### Post-trade, costs and ownership

| Rule | Exchange | Current value | Effective since | Changes in last 10 years | Tag/Source |
|---|---|---|---|---|---|
| Settlement cycle | All | Shares, closed-end funds, ETFs, warrants: T+2. Bonds: T+1. T = trade date. Cash and securities are settled between roughly 11:00 and 13:30 on T+2; members must allocate to clients before 13:00. | 2022-08-29 (VSD Decisions 109/QĐ-VSD and 110/QĐ-VSD of 2022-08-19). | Before 2022-08-29 the cycle was T+3; T+2 applies from 2022-08-29. The T+3 start date and whether T+3 held for all of 2016-10 to 2022-08 is not confirmed. A headline reports a central-counterparty (CCP) model targeted for the cash market in Q1 2027; not read. Decision 109/QĐ-VSD is listed on S19 as replaced in 2023 by Decision 15/QĐ-HĐTV. [Unverified → P1 check: read the current VSDC settlement rules; confirm T+3 applied 2016-10 to 2022-08, and read VSDC/SSC notices on CCP and any move to T+1] | [Fact S19] (Decision 109/QĐ-VSD dated 2022-08-19, effective 2022-08-29); [Assumption] (T+3 before, and T+2 content, S8 news); [Fact S1] (T+2 now) |
| Earliest resale of bought shares | All | Shares bought on T are credited by about 13:00 on T+2, so they can first be sold in the T+2 afternoon session (from 13:00). HOSE's own guide says buyers receive shares on the afternoon of T+2. | 2022-08-29. | Before 2022-08-29 the earliest sale was T+3. | [Assumption] (S8 news; HOSE guide S1 shows shares received in the afternoon of T+2) |
| Intraday round trip | All | Shares bought on T cannot be re-sold on T or T+1 because they are not yet credited; a sell order requires shares already held, and a buy order requires cash or margin deposit as required. Intraday round trips on the same shares are therefore not available to a cash account. | Follows from the two rows above. | Same as the two rows above. | [Assumption] (derived from S8 and S3; broker margin schemes not checked) |
| Exchange and VSDC fees | All | Exchange trading fee: 0.027% of traded value for shares on HNX and HOSE (UPCoM shares 0.018%); VSDC custody 0.27 VND per share per month. Prices exclude VAT where applicable. Fee schedule issued by the Ministry of Finance in Decision 1541/QĐ-BTC. | 2025-04-29. | Earlier schedule: Circular 127/2018/TT-BTC (effective 2019-02-15; its status and rates not read), amended by Circular 14/2020/TT-BTC. A search result reports Circular 125/2026/TT-BTC (effective 2026-10-06) keeps the Decision 1541 rates until a new document is issued; not read. Brokers say their fees include exchange/VSDC fees (see next row). [Unverified → P1 check: read Decision 1541/QĐ-BTC and Circular 127/2018/TT-BTC rate tables; confirm payer and rate history 2016-2025, including any Circular 101/2021/TT-BTC change] | [Fact S11] (decision, date, 0.027% for HNX); [Assumption] (HOSE 0.027%, UPCoM 0.018%, custody 0.27 VND, from S12 news; full-text page on thuvienphapluat.vn reportedly shows UPCoM 0.018% but returned HTTP 403) |
| Brokerage commission | All | Published listed-stock retail rates, as % of traded value: SSI 0.15% online and 0.25%-0.35% via staff by daily value (includes exchange fee); DSC 0.10% (advisory accounts) and 0.15%-0.30% (brokerage accounts, by daily value); KBSV 0.15%-0.20% online and 0.20%-0.25% other channels; VPS 0.20% online and 0.15%-0.30% other channels (includes exchange and VSDC fees). Overall observed range 0.10%-0.35%. These are tariff rates; promotional and negotiated rates are not covered. | SSI 2025-10-10; DSC 2025-08-20; KBSV 2026-07-22; VPS 2025-07-01. | Commission history not researched; modelling uses a fixed assumed rate. [Unverified → P1 check: the SSI page rendering of the staff-channel tiers was ambiguous in the fetched text; confirm SSI tiers on ssi.com.vn] | [Fact S13] (SSI); [Fact S14] (DSC); [Fact S15] (KBSV); [Fact S16] (VPS) |
| Securities transaction tax (sales) | All | 0.1% of the sale price per transaction (personal income tax on securities transfer), withheld by the broker. Applies to sales only, regardless of profit or loss. | 2026-07-01 under Law 109/2025/QH15, Article 13(2) (adopted 2025-12-10). | Law 109/2025/QH15 replaced Law 04/2007/QH12 on 2026-07-01. Before that the 0.1% rate was set by Circular 111/2013/TT-BTC as amended by Circular 92/2015/TT-BTC, reported by a secondary law-firm page only. Law 09/2026/QH16 (2026-04-24, effective the same day) amends Law 109/2025/QH15 (S18); its changes to Articles 12 and 13 were not readable. [Unverified → P1 check: read the consolidated Law (VBHN 112) Arts. 12-13 and read Circular 111/2013 and Circular 92/2015 text and the implementing decree for Law 109/2025, including the withholding mechanism] | [Fact S10] (current); history as marked |
| Dividend tax | All | Personal income tax on investment income, including dividends ("lợi tức cổ phần"), 5% for resident individuals, applied to income received. | 2026-07-01 under Law 109/2025/QH15, Article 12(1) and Article 3(3)(b). | Previously 5% under Law 04/2007 (not read in this task). The Law's Article 12(3) sets the timing at payment of income; whether stock dividends are taxed on receipt or on sale is not settled. Law 09/2026/QH16 (2026-04-24, effective the same day) amends Law 109/2025/QH15 (S18); its changes to Articles 12 and 13 were not readable. [Unverified → P1 check: read the consolidated Law (VBHN 112) Arts. 12-13 and read the implementing decree for Law 109/2025 and confirm the 5% history for 2016-2026 and the tax treatment of stock dividends] | [Fact S10] |
| Foreign ownership limit | All | Maximum foreign ownership in a public company depends on sector rules; sources disagree on the default when no sector rule applies (49% versus 50%). Decree 155/2020/NĐ-CP Article 139 is the base text; Decree 245/2025/NĐ-CP is reported by search results (unconfirmed) to have amended it. | Not pinned. | Not pinned. HOSE announced before go-live that foreign room would be reduced when a foreign buy order is entered (not when matched) and restored on cancel or reduction; whether it took effect as announced is not confirmed. [Unverified → P1 check: read Decree 155/2020 Art. 139 as amended by Decree 245/2025; use per-ticker foreign room from the exchange feed, not a statutory default] | [Unverified → P1 check: Decree 155/2020 Art. 139 and Decree 245/2025 text, default 49% vs 50%]; [Assumption] (announced room-accounting change, S7 news) |
| Short selling | All | Retail covered short selling is not confirmed available. Sell orders require the investor to hold enough securities when placing the order. A "secured short-selling" framework exists under Circular 120/2020/TT-BTC (borrowing through VSDC), but whether any broker offers it to retail clients is unknown. Treat short selling as not available to the owner. | Not pinned. | Not pinned. | [Unverified → P1 check: confirm in Circular 120/2020/TT-BTC and at named brokers that retail short selling is not offered; the sell-side holding requirement is stated in S3] |

### Status, calendar and corporate-event rules

| Rule | Exchange | Current value | Effective since | Changes in last 10 years | Tag/Source |
|---|---|---|---|---|---|
| Status flags | HOSE | WID/WFR/WOV warning flags (disclosure, financial reporting, other); CTR control; RES trading restriction; C&R control plus restriction; SUS suspension or halt; SLS suspended 25+ trading days; NWE newly listed share; NWN newly listed warrant. Ex-rights trade codes 01-07 and 16 mark which entitlements are not due. | S1 (Decision 22/QĐ-HĐTV, 2025-05-05). | Earlier flag set not read. [Unverified → P1 check: confirm flag set by date for 2016-2025] | [Fact S1] |
| Status flags | HNX | Not covered: no HNX flag list was read. | Not applicable. | Not applicable. | [Unverified → P1 check: HNX status flags and codes] |
| Status flags | UPCoM | Not covered: no UPCoM flag list was read. | Not applicable. | Not applicable. | [Unverified → P1 check: UPCoM status flags and codes] |
| Warning / control criteria | HOSE, HNX | Warning (Art. 36): paid-in capital under VND 30 billion, negative undistributed after-tax profit, qualified audit opinion, no AGM within 6 months of year-end, stopped main business 3+ months, no trading for 6 months. Control (Art. 37): two consecutive loss years, accumulated losses above paid-in capital, negative equity, no trading for 9 months. Decided within 5 working days. | 2025-05-05. | Earlier thresholds not read. Restricted-trading criteria, suspension triggers (reference to Securities Law Article 49) and voluntary delisting not read. [Unverified → P1 check: read Articles 14, 36-40 and the delisting articles of Decision 22/QĐ-HĐTV and the 2016-2025 predecessors] | [Fact S2] (see N1) |
| Warning / control criteria | UPCoM | Not covered: S2 covers listed securities only; UPCoM criteria were not read. | Not applicable. | Not applicable. | [Unverified → P1 check: HNX UPCoM regulation on warning, control, restriction and removal] |
| Delisting | UPCoM | Not covered: UPCoM deregistration rules were not read. | Not applicable. | Not applicable. | [Unverified → P1 check: UPCoM deregistration criteria and history] |
| Delisting | HOSE, HNX | Mandatory delisting criteria are in Decree 155/2020/NĐ-CP. One cited trigger: securities not traded within 90 days of listing approval (Art. 120). | Not pinned. | Not pinned. Full criteria and survivor-bias handling are not covered here. [Unverified → P1 check: read Decree 155/2020 Arts. 120-121 and obtain a historical delisting list from the exchanges] | [Fact S2] (see N1) |
| Exchange transfers | HOSE, HNX, UPCoM | Rules for moving between HOSE, HNX and UPCoM (reference price on the first day, band, suspension length) are not confirmed here. Reported precedent: shares moved from HOSE to HNX in 2021 kept the last HOSE close as the first-day reference price and used the HNX ±10% band. | Not pinned. | Not pinned. [Unverified → P1 check: read the transfer provisions in Decision 22/QĐ-HĐTV and the exchange notices; a backtest needs per-ticker listing-venue history] | [Unverified → P1 check: transfer rules text] |
| Ticker changes | All | No rule text found. | Not pinned. | Not pinned. [Unverified → P1 check: find the rule and an exchange-published ticker-change history; data providers may not map old tickers] | [Unverified → P1 check: ticker-change rule and history] |
| Trading calendar | All | Closed on Labour Code public holidays, announced per year by HOSE and HNX. Example: 2026 Tết Bính Ngọ closure Monday 2026-02-16 to Friday 2026-02-20, reopening 2026-02-23; trades of 2026-02-12 and 2026-02-13 settled 2026-02-23 and 2026-02-24 because settlement skips closure days. | Announced 2026-02-13 for the Tết 2026 closure. | Annual closure dates change each year. No source for the full 2016-2026 holiday list was read. [Unverified → P1 check: build the historical closure calendar from official HOSE/HNX announcements, not from Labour Code dates alone; compensatory working days are not trading days (Mon-Fri only per S2)] | [Fact S2] (Mon-Fri, Labour Code holidays); [Assumption] (Tết 2026 dates, S17 news) |

## Universe

Applies to every backtest, label and scan. Each rule is evaluated per session *d* with data timestamped on or before *d*. "Proposed default" values live in the single config file (spec §7) and are recorded in each pre-registration.

**Point-in-time membership.** A security is eligible on session *d* only if all of these hold:

1. It is a common share listed on HOSE or HNX, or registered on UPCoM, on *d*. The listing venue is taken from a dated venue-history table, so exchange transfers change band, tick, lot and fee on the transfer date. ETFs, covered warrants, closed-end funds and bonds are excluded. [Assumption] (the edge sought is in single stocks; other instruments have different rules per Market rules rows "Tick size" and "Settlement cycle")
2. It has at least 60 sessions of trading history on any venue before *d*. Reason: the longest feature look-back in the backlog is 60 sessions, and new listings trade under the first-day bands (Market rules "Price limit, first day / resumed trading"). [Assumption]
3. *d* is not within 5 sessions after a first trading day, a resumption after a 25+ session suspension, or an exchange transfer. Reason: on those days the ±20/30/40% bands apply and the reference price is not yet set by normal matching. [Assumption]
4. It does not carry a SUS, SLS, CTR, RES or C&R status on *d* (HOSE flag set per Market rules "Status flags"). Warning flags (WID/WFR/WOV) are allowed and carried as a feature. Reason: restricted stocks trade only in periodic auctions (Market rules "Restricted-status trading"), which this EOD fill model does not represent. [Assumption]
5. Where status history is missing (HNX and UPCoM flags are not covered; HOSE history before 2025-05-05 is not read), use this proxy: it is ineligible if it had zero volume on more than 2 of the last 20 sessions, or no trade on *d*. [Unverified → P1 check: obtain dated status-flag history per exchange; Market rules "Status flags" rows]
6. Liquidity filter (proposed default): median over the last 20 sessions up to *d* of daily traded value (price × volume, per session) ≥ max(VND 1 billion, P / c_open).
   - P is the fixed nominal grid size of the run (`## Capacity grid`), not the NAV-dependent P_d. Eligibility, labels, r_bench, b_d and label ranks therefore do not depend on any strategy's NAV path, and they are defined before any backtest. NAV_d is used only for order sizing.
   - c_open is the binding fill cap of `## Execution and fill model` rule 3.

   Reasons:
   - The floor removes names where a single retail order is material.
   - Tying the threshold to the binding fill cap means an order of size P fits the expected opening fill on a median day.
   - The VND 1 billion floor is a judgement call, because no liquidity distribution has been measured yet (spec §7). Phase 1 replaces it with a percentile of the distribution measured on development-period (D) dates only (`## Validation design`, calibration rule), and records it before any test.

   [Assumption]
7. Tick filter (proposed default): one tick ÷ close on *d* ≤ 1%. With the current ticks (Market rules "Tick size"), this means a price of at least VND 1,000 on HOSE and VND 10,000 on HNX/UPCoM. Reason: a one-tick move is charged as slippage on each side, and above 1% it alone consumes a large part of a plausible 5–20 session edge. [Assumption]

Each run reports the eligible count per date. If its median is below 30, every verdict carries `THIN UNIVERSE`. Reason: the c_open-based floor can leave few names at larger grid sizes. [Assumption]

**Identity.** Tickers are mapped to a permanent internal security id through a dated ticker-change table. If no table can be built, every ticker change creates a false delisting and a false new listing, and this is reported as a data limitation. [Unverified → P1 check: Market rules "Ticker changes"]

**Survivorship bias.** This is gated on P1 check #1 in data-sources.md `## P1 checks (consolidated)` (fetch a known delisted ticker), and on Market rules "Delisting" (historical delisting list):

- If the chosen source returns delisted tickers for the whole window, no warning is needed. The coverage test (tickers tested, tickers found) is stored with the data version.
- If it does not, every backtest output, scorecard and Telegram verdict carries the label `SURVIVORSHIP-BIASED: universe excludes securities delisted before <snapshot date>`, together with the count of known delistings by year from the exchange list, if one was obtained.
- Whether a survivor-only result may be promoted to Level 2 is open; the proposed default is to allow it, with the label kept on the verdict permanently. [Owner decision needed]
- No paid source is yet verified to close this gap (data-sources.md `## Material gaps`, row "Delisted tickers and ticker changes").

**Fundamentals gate.** No hypothesis that uses financial-statement data may be run until P1 check #4 (publication or filing date field) passes for the source used. Even then, a value is usable on *d* only if its publication timestamp is ≤ the close of *d*−1. If only period-end dates exist, the hypothesis stays at Level 0. [Unverified → P1 check: data-sources.md P1 #4]

## Targets and labels

**Timing.**
- Signal date *t*: features use data up to and including the close of *t*.
- Entry session *e* = *t*+1. Horizon *h* ∈ {5, 10, 20} sessions, with the clock starting at entry (spec §6).
- Nominal exit session *x* = *e*+*h*. Realised exit session *x*′ is the session the exit actually completes, after locks, suspensions and the settlement rule.
- *x*′ ≤ *x* + L always holds, with L = 10 sessions (the delayed-exit cap). At *x* + L, any remainder is closed by the terminal rule in `## Execution and fill model` rule 8.
- Reason for L = 10: two weeks covers most lock runs while keeping the purge gap bounded. [Assumption]

Sessions are counted on the verified trading calendar (Market rules "Trading calendar").

**Prices.** Baseline: entry and exit at the session's opening price as defined in `## Execution and fill model` (HOSE ATO; HNX/UPCoM first continuous match). Sensitivity: entry and exit at the session close (ATC on HOSE/HNX).

**Forward net return** for stock *i*:

```
r_i(t,h) = [ P_exit · F_i(e,x′) · (1 − c_sell) + U_i(e,x′) + D_i(e,x′) − T_i(e,x′) ] / [ P_entry · (1 + c_buy) ] − 1
```

- P_entry is the fill price after slippage. P_exit is the realised exit fill price after slippage, or the terminal price from `## Execution and fill model` rule 8.
- F_i(e,x′) is the cumulative split/bonus/stock-dividend adjustment factor. It covers ex-dates in (e, x′] whose new shares are listed and sellable by *x*′.
- U_i(e,x′) is the value of new shares not yet listed at *x*′, per original share, treated exactly as in NAV (`## Execution and fill model` rule 8):
  - if they list and can be sold at a fillable session ≤ *x* + L, they are sold there at that fill price after slippage;
  - otherwise they are valued at P_exit × (1 − τ_v), where τ_v is the venue haircut of rule 8.

  No price after *x* + L is used.
- D_i is the cash dividend per original share with ex-date in (e, x′], net of 5% dividend tax (Market rules "Dividend tax").
- T_i is the stock-dividend tax of `## Cost model`: 5% of the market value of new shares at their ex-date.
- c_buy and c_sell are the proportional costs of `## Cost model`, with the 0.1% sales tax in c_sell.

Illustrative formula, not code.

**Corporate actions.** Adjustment factors come from a dated corporate-action table cross-checked against raw closes (data-sources.md P1 #2 and #10). If the source supplies only an adjusted series with an undocumented method, labels use it, and the data version records `adjustment=provider-undocumented`.
- For model-training labels only, any (i, t) window that contains an ex-date the raw and adjusted series cannot reconcile is dropped, and the drop count is reported.
- The backtest NAV never drops such a position. It keeps holding the position, values it with the provider's adjusted series, and flags it `ca_unreconciled`.

[Unverified → P1 check: data-sources.md P1 #2, #10]

**Benchmark.**
- Primary, per label: r_bench(t,h) = the equal-weighted mean of the gross forward returns of all stocks eligible at *t*. It uses the same entry and exit prices and the same lock, suspension, cap-L and terminal rules as `## Execution and fill model`, but no costs and no participation caps. Stocks locked at entry are left out of that date's cohort. [Assumption]
- Primary, daily (b_d, used by G1, G4, G7, G9 and the metrics): a benchmark portfolio run on exactly the strategy's rebalance schedule (`## Default risk settings`, portfolio construction).
  - It is continuously invested and uses the strategy's cycle and start offset. Its target is equal weight across every stock eligible at the signal date.
  - At each sell session it sells only what the target requires: names no longer eligible, and the overweight part of names still held.
  - At the following buy session it buys underweight and newly eligible names with settled cash only (rule 6).
  - It uses the fill model's lock, suspension, cap-L and terminal rules, with no costs and no participation caps. A slice that is locked or otherwise unfillable stays in cash until the next rebalance.
  - b_d = BNAV_d / BNAV_{d−1} − 1, marked at closes. For G5, b_d is rebuilt with ATC fills.
  - What the excess r_d − b_d does and does not isolate: it removes the market, universe and survivorship effects that both portfolios share. It does not isolate stock selection alone. It also contains the exposure difference: the strategy holds cash during settlement waits, when participation caps bind, and when slots are empty, while b_d stays nearly fully invested. Any timing effect of the rebalance schedule also remains.
  - Diagnostic, not a gate: the exposure-matched excess, A × mean(r_d − β̂ · b_d). Here β̂ = ē_S ÷ ē_B, and ē_S and ē_B are the mean over the evaluation period of each portfolio's gross long value ÷ NAV at the close. It is reported next to every excess figure.

  This replaces the round-1 overlapping-cohort design. [Assumption]
- Reason for the benchmark design: it has the same universe (and so the same survivorship bias) and the same fill timing, and leaving out costs makes it harder to beat. [Assumption]
- Secondary, for context only: the VN-Index price return. It is HOSE-only and cap-weighted, and whether it includes dividends is unverified. [Unverified → P1 check: confirm whether a total-return VN-Index series is available from the source]

**Default target.** The default target is the cross-sectional percentile rank of r_i(t,h) among stocks eligible at *t*. Because r_bench(t,h) is common to all stocks on date *t*, this rank equals the rank of the excess y_i(t,h) = r_i(t,h) − r_bench(t,h). y is used in portfolio-level and excess-return metrics. The primary horizon is *h* = 10; *h* = 5 and *h* = 20 are reported as well. Reasons:
- The rank removes market direction, which a long-only stock picker cannot control. It also matches spec §6.
- 10 is the middle of the owner's 5–20 range.
- Exact-price targets are not used (phase-0.md §6).

[Assumption]

Absolute returns and downside-aware rank (return ÷ 20-session realised volatility) are reported only as diagnostics.

**Unfillable labels.**
- If the entry is unfillable under the fill model (e.g. the open is locked at the ceiling), the label is missing for that (i, t) and counted. It is never back-filled with another price.
- If the exit is unfillable, it is retried at each next session up to *x* + L, and the realised price is used. At *x* + L, the terminal rule applies. This keeps the bad outcomes in the sample while bounding the label end.

**Overlapping labels and leakage.**
- With daily signals, consecutive *h*-session labels share *h*−1 sessions, so they are serially correlated and the effective sample size is about the number of dates ÷ *h*. [Assumption]
- Purge gap G = *h*_max + L + 2 = 32 sessions. A training signal date *t* must satisfy *t* ≤ *t*_test − G, where *t*_test is the first signal date of the test block. Then every training label's realised end *x*′ ≤ *t* + 1 + *h*_max + L falls strictly before *t*_test. This drops every observation whose realised, possibly delayed label could overlap the test period, following the purging idea in López de Prado (S26). [Assumption]
- The same G separates the development period D from the held-out period H (`## Validation design`).
- Embargo: in the anchored walk-forward, training always precedes testing, so no embargo after the test block is needed. One G is used for all three horizons, so they share folds.
- Significance tests use non-overlapping evaluation dates (every *h*-th signal date), or a HAC standard error with lag *h*−1 when daily dates are used. [Assumption]

## Execution and fill model

Applies to entries and exits alike (spec §6). This is a simulation of a manual retail account trading in round lots. The owner is assumed to be a domestic resident individual, so foreign-room limits are ignored. [Assumption]

**Rule as of date.** Every exchange parameter (sessions, band, tick, lot, settlement cycle, fees, tax) is looked up by (exchange, date) in a dated rules table built from `## Market rules`. Where a row's value for a date is tagged Assumption or Unverified, the model uses the conservative candidate and sets `rule_unverified = true` on the trade:

| Parameter | Conservative choice where unverified |
|---|---|
| Daily band | Use the band given; a lock is detected within 1 tick of the computed limit (below). Where two candidate bands exist for a date (e.g. UPCoM before 2017-06-20), test both, and treat the trade as locked if either says locked. |
| Tick | The larger candidate tick. |
| Lot | The larger candidate lot. HOSE uses 100 shares for all dates: the earlier 10-share lot is Assumption-tagged in Market rules "Lot size", and the larger lot loses more to rounding. |
| Settlement | The longer cycle: T+3 before 2022-08-29, T+2 from that date (Market rules "Settlement cycle", "Earliest resale"). |
| Sales tax | 0.1% throughout; no lower candidate is known. |
| Opening mechanism, HNX/UPCoM | No opening auction on any date; see below. |
| UPCoM session start | Conflict 09:00 vs 09:15 (Market rules "Trading sessions", UPCoM); not material for EOD; covered by the extra opening slippage. |

Each run reports the share of trades with `rule_unverified = true`. `## Pass/fail gates` G12 limits it.

**Order timing.** The owner places orders after the *t* close data are published and before the *e* open. [Assumption] (spec §6 designer's call)

**Baseline fill price.**
- HOSE: the ATO auction price of session *e* (09:00–09:15, Market rules "Trading sessions" HOSE).
- HNX and UPCoM: this is a deviation from spec §6, which assumes an opening auction. There is none on HNX or UPCoM from 2025-05-05 (Market rules "Trading sessions" and "Order types" HNX/UPCoM). Their baseline is the first continuous-matching price, as given by the EOD open field, plus the extra opening slippage in `## Cost model`. [Assumption]
- The opening mechanism before 2025-05-05 is not verified. The model treats HNX and UPCoM as having no opening auction on all dates and flags pre-2025-05-05 HNX/UPCoM fills as `rule_unverified`. [Unverified → P1 check: HNX and UPCoM opening mechanism 2016–2025]
- Whether each source's "open" field is the ATO match on HOSE and the first match on HNX/UPCoM is [Unverified → P1 check: compare the source open with the HOSE published ATO price for a sample of D-period days].

**Sensitivity fill price.**
- HOSE and HNX: the session close, which is the ATC match (Market rules "Reference price" HOSE: closing price = ATC match).
- UPCoM has no call auction, and what its EOD "close" represents is unverified, so the close field is used and every UPCoM ATC fill is flagged. [Unverified → P1 check: define the UPCoM close field per source]

**Fill rules**, applied in order to each intended order of Q shares:

1. **Not trading.** If the stock is suspended, halted or has zero volume on the session, there is no fill. An entry is cancelled and not chased. An exit is retried at each next session up to *x* + L, then rule 8 applies. [Assumption]
2. **Price limits.** Ceiling and floor are reference × (1 ± band) per Market rules "Daily price limit". Rounding to the tick grid is unverified, so a price within 1 tick of a limit counts as at the limit. [Unverified → P1 check: limit-price rounding rule in Decision 22/QĐ-HĐTV]
   - The reference price is the prior close for HOSE/HNX. On ex-dates, the S2 Art. 31 adjustment is used when the corporate-action table allows it. Otherwise the ex-date is flagged and the band is applied to the provider's reference field, if any.
   - For UPCoM the reference is the prior-day VWAP of round-lot continuous matches (Market rules "Reference price" UPCoM, Assumption). It is computed from the provider's reference field if present; otherwise prior close is used and the trade is flagged.
   - A buy at the open is unfillable if open ≥ ceiling − 1 tick. A sell at the open is unfillable if open ≤ floor + 1 tick.
   - For the ATC sensitivity, a buy is unfillable if close ≥ ceiling − 1 tick, and a sell if close ≤ floor + 1 tick.
   - Reason: EOD data cannot show the queue at a locked price. Assuming zero fill is the conservative reading of spec §6. [Assumption]
3. **Participation cap.** One cap is used for both sizing and filling:

   ```
   c_open  = q × a_open      c_close = q × a_close
   ```

   - q = 10% is the share of the auction (or of the opening trades) the order may take.
   - a_open and a_close are the auction's share of total daily matched volume. On HNX/UPCoM, a_open is the share of daily volume traded at the first continuous-match price.
   - Provisional defaults: a_open = a_close = 2%, so c_open = c_close = 0.2% of daily volume.
   - Reason: EOD data has no auction volume. Taking a tenth of an assumed small auction keeps the order from setting the auction price. [Assumption]
   - **Precondition.** a_open and a_close must be measured before any held-out run. Measurement uses HOSE session statistics (and HNX/UPCoM first-trade volume) for a sample of stocks on D dates only, and the values are recorded in the pre-registration field `auction_share`. If they are not measured, G12 fails. [Unverified → P1 check: source of ATO/ATC matched volume and first-trade volume per session]
   - Pre-trade sizing: Q = min(P_d ÷ price, c_open × 20-session median volume up to *t*), rounded down to the lot. Use c_close for the ATC sensitivity.
   - At fill: filled quantity = min(Q, c_open × V_e) at the open, or min(Q, c_close × V_e) at the close. V_e is the session's total matched volume.
   - V_e must exclude put-through volume, which a retail order cannot access. If the source does not separate it, V_e is used as given and the run is flagged. [Unverified → P1 check: whether source volume includes put-through and odd lots]
4. **Lots.** The filled quantity is rounded down to the round lot in force. If it rounds to zero, there is no fill.
   - An unfilled entry remainder is cancelled. An unfilled exit remainder is retried at each next session under rules 1–3, up to *x* + L, then rule 8 applies.
   - Orders above the HOSE per-order cap of 500,000 shares are split into several orders. They are filled under the same cap.
   - Odd-lot shares (1–99) arise only from corporate actions. They are held, marked at the close, and sold at the exit with an extra 1% price haircut. Reason: odd lots trade in a separate, thinner book with limit orders only (Market rules "Odd-lot trading"), and before 2025-05-05 they could not be sold in HOSE auctions. [Assumption]
5. **Settlement-delayed exits.** Shares bought on session *e* can be sold no earlier than:
   - from 2022-08-29: the ATC of *e*+2, or the open of *e*+3;
   - before that date: the ATC of *e*+3, or the open of *e*+4.

   This follows Market rules "Earliest resale of bought shares" (credited around 13:00 on T+2) and "Intraday round trip". An exit signal (stop, invalidation) that falls earlier is delayed to that session, and that session becomes its nominal exit *x* for the L cap. Horizon exits with *h* ≥ 5 are never affected.
6. **Sale proceeds.** Proceeds are available for new buys only from the settlement date of the sale. For an open-auction buy, that means from the open of the sale session + 3 (from 2022-08-29) or + 4 (before). For a close buy, it means from the ATC of the sale session + 2 or + 3. Reason: whether brokers' advance-on-sale facilities apply, and what they cost, is not verified. [Assumption]
   - This creates a cash wait of s sessions between each sell session and the next buy session (s = 3 or 4 for opens). The cash drag is about s ÷ (h + s): about 3/8 of the time at *h* = 5 and 3/23 at *h* = 20.
   - A robustness run with proceeds usable immediately (advance-on-sale assumed, with no fee) is reported alongside. It is not a gate.
7. **Fill price after slippage.** Buy = fill price × (1 + s), rounded up to the tick and capped at the ceiling. Sell = fill price × (1 − s), rounded down to the tick and floored at the floor. *s* is given in `## Cost model`.
8. **Terminal rule.** At *x* + L, any unsold remainder is closed at (last traded close up to *x* + L) × (1 − τ_v), and flagged `exit_forced`.
   - If the stock is suspended or halted at *x* + L, or has not traded in the last 5 sessions, the 100% case below applies and takes precedence.
   - Otherwise (the failure was limit-locking or thin volume), τ_v = 3 × the venue's daily band in force: HOSE 21%, HNX 30%, UPCoM 45%. The bands are from Market rules "Daily price limit"; the UPCoM band is Assumption-tagged there, so UPCoM terminal values carry `rule_unverified`. Reason: three more floor moves beyond the last print is a conservative allowance for a stock that could not be sold for two weeks. [Assumption]
   - Suspended or halted at *x* + L, or not traded in the last 5 sessions: τ_v = 100%, and the remainder is valued at 0. Reason: a long suspension may end in delisting, and using the later resumption price would be look-ahead. [Assumption]
   - Every report also gives a sensitivity with τ = 100% for all forced exits. This is a robustness run, not a trial.
   - Exchange transfer while held: the position continues on the new venue under that venue's rules as of date, and the L clock keeps running.
   - Delisting with no successor venue while held: the value is set to 0 on the delisting date and flagged `delisted_held`.
   - New shares from bonus issues or stock dividends: they are sold at the first fillable session after their listing date, if that is ≤ *x* + L. Otherwise they are valued at P_exit × (1 − τ_v) and flagged. Labels use the same rule (`## Targets and labels`, U_i). [Unverified → P1 check: typical listing lag of new shares from bonus issues and stock dividends]
   - Reason: every position, label and NAV contribution then ends by *x* + L, which the purge gap G relies on.

**Inputs end-of-day data lacks, and the conservative proxy used for each**

| Missing input | Why it matters | Proxy used | Check |
|---|---|---|---|
| ATO/ATC matched volume; HNX/UPCoM first-trade volume | Caps sizing and fills at the open and close | c = 10% × assumed 2% of daily volume = 0.2%, until measured on D dates | [Unverified → P1 check: HOSE session statistics; precondition in G12] |
| Queue and depth at ceiling/floor | Whether a locked order fills | Zero fill within 1 tick of the limit | none possible from EOD |
| Whether "open" is an auction price (HOSE) or the first trade (HNX/UPCoM), and its time | Opening price realism | Open field + extra opening slippage on HNX/UPCoM | [Unverified → P1 check: compare with exchange ATO prices] |
| Reference, ceiling and floor prices | Lock detection | Provider reference field, else prior close; ex-dates and UPCoM flagged | [Unverified → P1 check: P1 #2] |
| Bid-ask spread | Slippage | Corwin–Schultz high-low estimator (S29), floored at 1 tick | none; estimator noise covered by G6 cost stress |
| Status-flag history (HNX, UPCoM, pre-2025 HOSE) | Universe and tradability | Zero-volume rule in `## Universe` item 5 | [Unverified → P1 check: status history] |
| Put-through and odd-lot split of volume | Participation base | Volume as given; run flagged | [Unverified → P1 check: field definitions] |
| UPCoM close definition | ATC sensitivity | Close field; flagged | [Unverified → P1 check] |
| Listing date of new shares from corporate actions | When they can be sold | Terminal valuation at P_exit × (1 − τ_v) | [Unverified → P1 check: listing lag] |

## Cost model

All costs are per side, as a share of traded value, unless stated otherwise. Values come only from `## Market rules`.

| Component | Proposed default | Reason / source |
|---|---|---|
| Commission | 0.35% of traded value per side | Top of the published range 0.10%–0.35% (Market rules "Brokerage commission", S13). Spec §7 asks for the upper range. SSI and VPS state their rate includes exchange fees (S13, S16), so no separate exchange fee is added. |
| Commission sensitivity | 0.20% and 0.15% | 0.20% = the highest online-channel rate seen (KBSV, VPS: S15, S16); 0.15% = a common online rate (S13, S15). Reported only; gates use the default unless the owner sets their own rate before pre-registration. |
| Owner's broker rate | optional setting | If the owner's rate excludes exchange fees, add 0.027% (HOSE/HNX) or 0.018% (UPCoM) per Market rules "Exchange and VSDC fees" (Assumption-tagged rates). |
| Sales tax | 0.1% of sale value, every sale | Market rules "Securities transaction tax" [Fact S10]; same rate assumed before 2026-07-01 per that row's history. |
| Dividend tax | 5% of cash dividends | Market rules "Dividend tax" [Fact S10]. |
| Stock-dividend tax | 5% of the market value of new shares at the ex-date | Treatment is unsettled (Market rules "Dividend tax"), so the conservative reading is taken; it enters labels as T_i. [Assumption] |
| Custody | 0.27 VND per share per month held | Market rules "Exchange and VSDC fees" (Assumption-tagged); negligible, included for completeness. |
| Slippage *s* | max(1 tick ÷ price, ½ × CS20) + 0.10% | CS20 = the 20-session mean of the daily Corwin–Schultz spread estimate (S29), negatives set to 0. The window ends at the signal date *t* for entries and at the session before the exit attempt for exits. The fixed 0.10% stands for unmodelled impact and auction uncertainty. [Assumption] |
| Extra opening slippage, HNX/UPCoM | +0.10% at the open | No opening auction, so the first match may be a thin early trade. [Assumption] |
| Uninvested cash | earns 0 | No verified VND money-market series sourced. [Assumption] |

History: commission history was not researched, so the fixed rate is used for all dates. [Assumption] (Market rules "Brokerage commission")

## Validation design

**History available.** N = the number of sessions in the verified usable history. That is the latest of the start dates at which, for the chosen source:
- all three exchanges are covered (P1 #3),
- the adjustment method is verified (P1 #2), and
- the trading calendar is verified (Market rules "Trading calendar").

N is recorded in the data version. [Unverified → P1 check: data-sources.md P1 #2, #3; history depth is `unknown` for every scorecard row]

**Split rule.** History is split into three consecutive parts:

```
[ D: development | gap: 31 sessions | H: held-out ]
```

- H holds the last H_len = max(32 × *h*_max, ⌈0.2 × N⌉) = max(640, ⌈0.2 × N⌉) sessions. Its first signal date *t*_H is a project-wide constant, stored in the data-version manifest for each `data_version`. Every pre-registration record copies it. It is never recomputed from N, and no family can move it.
- The last D signal date is *t*_D = *t*_H − G, with G = 32 (`## Targets and labels`, purge gap). The G − 1 = 31 sessions strictly between *t*_D and *t*_H are a gap with no signal dates.
- D is everything up to *t*_D, so |D| = N − H_len − 31.
- Every D label and every D backtest position ends by *t*_D + 1 + *h*_max + L < *t*_H. Gap prices may be used only to complete those exits.
- To guarantee this, there are no keep decisions at the boundary. Let B be the last buy session whose signal date B − 1 ≤ *t*_D, so B ≤ *t*_D + 1. Every open position, including positions kept from earlier cycles and every benchmark holding, is sold at the next scheduled sell session B + *h* under the normal rules, with the 2K buffer switched off. The realised exit is then ≤ B + *h* + L ≤ *t*_D + 1 + *h*_max + L = *t*_H − 1. The same rule applies at the end of every training window whose backtest is used for tuning, relative to that fold's last training signal date *t*_test − G.
- Minimum: N ≥ 1,600 sessions. Below that, no strategy can reach Level 2, and every verdict reads "insufficient history".

Reasons:
- 640 sessions (about 2.6 years) give 31 complete non-overlapping 20-session labels in H, which meets G11 and spans at least one market regime change. The arithmetic: signals fall at *t*_H + 20k, and each must exit by *t*_H + 20k + 1 + 20 + L = *t*_H + 20k + 31 ≤ *t*_H + 639, so k ≤ 30, which gives 31 signal dates. The minimum for 31 periods is 30 × *h*_max + 1 + *h*_max + L + 1 = 632; for G11's 30 periods it is 612. 640 is used.
- At N = 1,600, |D| = 1,600 − 640 − 31 = 929, which still allows the 500-session initial training window and 3 test folds (below).

[Assumption]

Provisional default until Phase 1 confirms N: history from 2016-10-27 (the Market rules window) to the snapshot date, at about 250 sessions per year. That gives N ≈ 2,500, H_len = max(640, 500) = 640, and |D| ≈ 2,500 − 640 − 31 = 1,829. H then contains the KRX go-live (2025-05-05), so held-out results reflect current matching rules. [Assumption]

**Walk-forward inside D.**
- Anchored, expanding window. The initial training window is 500 sessions; test blocks are 125 sessions (about 6 months), contiguous, with a step of 125.
- Folds = ⌊(|D| − 500 − (G − 1)) / 125⌋. Training signals occupy sessions 1–500, and the first test signal is session 500 + G = 532, so 531 sessions come before the first test block. That gives ⌊(929 − 531) / 125⌋ = 3 at N = 1,600, and ⌊(1,829 − 531) / 125⌋ = 10 at the provisional N ≈ 2,500. Three folds need |D| ≥ 531 + 375 = 906, i.e. N ≥ 906 + 640 + 31 = 1,577; the minimum of 1,600 covers it.
- For each fold, training signal dates satisfy *t* ≤ *t*_test − G (`## Targets and labels`).
- Reasons: expanding windows use all past data, which suits a short market history. Each 125-session test block holds about 12 non-overlapping 10-session periods. [Assumption]
- NAV across folds: the OOS series is one continuous simulated portfolio across the contiguous test blocks. At each block start, the model or parameters are swapped for that fold's. Positions open at a block boundary are kept and exit under their own entry-time rules.
- Results are reported per fold and as the concatenated OOS series.

**Tuning without contamination.**
- Parameters for a fold are chosen using only that fold's training window. The last 20% of the window serves as the validation slice, with the same gap G before it. [Assumption]
- Simple rules use a small parameter grid stated in the pre-registration. Each grid point is one trial.
- Test blocks of D are never used for selection, and H is never used for anything before freezing.
- ML models (Phase 3) fix random seeds and record them.

**Calibration rule and H masking.**
- Every calibration uses D dates only. This covers the liquidity-floor percentile, the auction shares a_open and a_close, the session count A, the Corwin–Schultz parameters, and any Phase 1 measurement that feeds a setting.
- Every run at the measured auction share a supersedes runs at the provisional a, because the floor, universe and sizing change with it. G1–G3 OOS evidence must come from runs at the measured a. Runs at the provisional a still count as trials in N_trials. [Assumption]
- The data loader masks every session ≥ *t*_H by default.
- It unmasks H only when all of these hold. If any fails, it refuses.
  - It is given a pre-registration record whose hash appears in a git commit (`prereg_commit`).
  - The configs to run are exactly the record's `batch` list of config hashes, all in one invocation. `code_version`, `data_version` and `gates_version` equal the record's.
  - The record's *t*_H equals the project-wide *t*_H in the data-version manifest.
  - The family's look counter in the trial registry is 0. The loader increments it atomically, once for the whole batch, before any H data is returned.
- The loader records the commit id, the run time, the batch hashes and the new look count in the trial registry. The counter lives in the registry, not in the hashed record, so incrementing it never changes the record's hash.
- Limitation: git commit dates can be set by the author, so the commit only shows that the record existed in the repository. It does not prove when the record was made. The guarantee rests on the hash match and the look counter, together with the owner's discipline. [Assumption]

**Pre-registration record.** It is written and hashed before H is touched, committed to git, and stored append-only. Fields:

| Field | Content |
|---|---|
| `strategy_id`, `version`, `hypothesis_id` | `hypothesis_id` must be a backlog id (H1–H8 in `## Hypothesis backlog`, or a later entry added to that table before any run). Any change to rules or parameters gives a new `version` under the same `hypothesis_id` while the economic idea is unchanged. |
| `rules` | Plain-text entry, exit, ranking, sizing and risk rules |
| `parameters` | Every value, including universe, fill and cost settings (config hash of the baseline run) |
| `batch` | Config hashes of every run in the single H look (`## Validation design`, held-out looks) |
| `horizon`, `rebalance` | *h*, rebalance schedule, start offsets |
| `split` | *t*_D, G, *t*_H (copied from the data-version manifest), H_len, N; a statement that all D labels and positions end before *t*_H |
| `auction_share` | Measured a_open and a_close, the D-date sample used, and the source |
| `gates_version` | The gate table below, by hash; gates are never edited after freezing |
| `data_version` | Source, snapshot id and date, content hash, survivorship status, adjustment status |
| `code_version` | Git commit of the backtester |
| `trial_count` | Family count (rows for this `hypothesis_id`) and global count (all rows) at freeze |
| `frozen_at`, `author`, `seeds` | Timestamp (UTC+7), owner, random seeds |
| `prereg_commit` | Git commit holding this record, made before the H run |

**Trial registry.**
- Every backtest run (any change in rules, parameters, universe, horizon, cost or fill setting) is one row: config hash, data version, code version, timestamp, summary metrics, and the full daily OOS net-excess return series. Rows are never deleted (spec §4).
- The registry also holds one append-only H-look counter per `hypothesis_id`. It starts at 0 and is never reset.
- Families: a `hypothesis_id` comes only from the backlog table. Rule changes that keep the same economic idea stay in the same family. A new backlog row needs an owner-approved commit that states why its economic idea differs from every existing row; a near-duplicate row is not allowed. [Owner decision needed]
- The count used for the multiple-testing adjustment is N_trials = all rows sharing the `hypothesis_id`, including failed and abandoned runs. The cross-trial variance of Sharpe ratios also comes from those rows. Both feed the deflated Sharpe ratio (S21).
- Every verdict reports the global trial count (all rows) next to the family count, the global number of H looks taken across all families, and the DSR recomputed with the global count and the global cross-trial Sharpe variance. G1 uses the stricter (lower) of the family and global DSR.
- The stored series feed the SPA test (S24) and PBO (S22).
- Clustering trials into "independent" groups is allowed only if the clustering rule is itself pre-registered. Otherwise all rows count. [Assumption]
- Pre-registered robustness reruns (start-offset variants, cost sensitivities, capacity-grid sizes, the G8 restricted rerun) are logged with `robustness = true`. They do not count as trials because they are not used for selection. [Assumption]

**Held-out looks.** H is evaluated once per `hypothesis_id`. The one look is a single batch, listed in the record's `batch` field and run under one increment of the family's look counter. The batch contains:
- the baseline run;
- the G5 ATC run;
- every G10 capacity-grid size;
- the G8 restricted rerun;
- the pre-registered robustness runs (τ = 100%, immediate proceeds, cost sensitivities).

After that look, H is contaminated for the whole family: no version of it may be evaluated on H again, and promotion of any later version needs forward paper data (Level 3 path) or a new held-out period of fresh data. Reason: a second look roughly doubles the chance that noise passes the H gates. [Assumption]

## Pass/fail gates

These are pre-registered and versioned as `gates_version = 1`. All of them must pass for Level 1 → Level 2.
- "OOS" means the concatenated walk-forward test blocks in D; "H" means the held-out period.
- All returns are net of `## Cost model` costs, at the configured position size, using the baseline fill. Excess is measured against b_d (`## Targets and labels`).
- Thresholds are never tuned on test data.

| # | Gate | Threshold | One-line reason |
|---|---|---|---|
| G1 | Deflated Sharpe ratio of OOS daily net excess returns, computed twice: with the family N_trials and Sharpe variance, and with the global ones | The lower of the two DSRs ≥ 0.95 | DSR (Bailey & López de Prado, S21) estimates the probability that the true Sharpe exceeds zero after adjusting for the number of trials and non-normal returns; 0.95 matches a one-sided 5% test. The 0.95 level is a convention. [Assumption] |
| G2 | Hansen SPA test, all trials in the family versus the benchmark (loss = −net excess return), stationary bootstrap (S27), 1,000 resamples, mean block length = *h* | p ≤ 0.05 | SPA (S24) builds on White's Reality Check (S23): it tests whether the best of many tried rules beats the benchmark by more than luck. Harvey–Liu–Zhu (S25) argue that single-test t ≈ 2 hurdles are too lax when many strategies are tried. The 5% level and the block length *h* (matching label overlap) are judgement calls. [Assumption] |
| G3 | Probability of backtest overfitting (CSCV, S22) on the family's trial matrix, 16 sub-samples | PBO ≤ 0.25 | PBO is the chance that the in-sample best configuration ranks below the median out of sample; above 0.5, selection is worse than random. 0.25 leaves margin, and the family must have ≥ 2 trials, otherwise the gate is reported as N/A. [Assumption] |
| G4 | Held-out net excess return (one look per family) | All three: annualised net excess on H > 0; H information ratio ≥ 0.5 × OOS information ratio; one-sided 80% stationary-bootstrap lower bound (S27, block *h*) of H mean daily net excess > 0 | G1–G3 carry significance on the longer OOS series; H is a single-look consistency check. The 80% bound limits pure-noise passes to about 20%, against about 50% for the sign alone, and half the OOS ratio tolerates decay. [Assumption] |
| G5 | Execution sensitivity (ATC entry and exit) | Annualised net excess > 0 on OOS and on H, against b_d rebuilt with ATC fills | Owner decision 4 and spec §6: an edge that exists only at one fill assumption is rejected. |
| G6 | Cost stress: slippage × 2 | Annualised net excess > 0 on OOS | Spread estimator noise and unknown auction impact; Novy-Marx & Velikov report that trading costs always reduce anomaly profits [Fact S30]. The factor 2 is a judgement call [Assumption]. |
| G7 | Sub-period stability | OOS split into calendar years. A year counts only if it has ≥ 125 OOS sessions; a shorter first or last stub is merged into the adjacent year. Net excess > 0 in ≥ 2/3 of counted years, and no counted year contributes > 50% of cumulative OOS excess | Guards against one regime carrying the result; the 125-session minimum avoids judging half-empty years. [Assumption] |
| G8 | Liquidity buckets | A restricted robustness rerun: on each signal date, only the top tercile of eligible stocks by 20-session median traded value at *t* is eligible, and everything else is unchanged. Annualised OOS net excess (against b_d rebuilt on the same restricted universe) > 0 | An edge confined to illiquid names is most likely a cost or fill-model artefact. A rerun is used rather than trade attribution, because attribution mixes in the portfolio effects of other names. [Assumption] |
| G9 | Maximum drawdown (net, daily NAV) | Strategy MDD ≤ benchmark MDD over the same OOS period, and over H | A long-only strategy that adds drawdown beyond holding the universe gives a personal account no risk benefit. [Assumption] |
| G10 | Capacity | G1, G4, G5, G6 and G12 pass at the configured position size (`## Capacity grid`) | Spec §4 and §7; the verdict also states the largest grid size at which they pass. |
| G11 | Minimum sample | ≥ 100 round-trip trades in OOS; ≥ 30 in H; ≥ 30 complete non-overlapping *h*-period labels in H (H_len = 640 gives 31 at *h* = 20; see `## Validation design`) | Fewer observations make every statistic above unreliable. The counts are rules of thumb. [Assumption] |
| G12 | Data integrity | All of: (a) entry fill rate ≥ 80% of intended entry shares; (b) outcome-sensitive unverified trades ≤ 20% of trades; (c) trades with `exit_forced` ≤ 5%; (d) `auction_share` measured on D dates and recorded; (e) survivorship label shown if applicable. A trade is outcome-sensitive only if re-simulating it with each candidate value of every unverified rule it touches flips fill versus no fill, flips its lock or terminal status, or changes its filled notional by more than 5%. Differences that come only from lot rounding (e.g. HOSE 10 vs 100 shares before 2021) or only from price (slippage tiers, the HNX/UPCoM opening-mechanism candidates, which share the same measured a and differ only in extra slippage) are not counted here; G6 covers them. Reason for 5%: a smaller change in notional moves the trade's P&L contribution by less than 5% of itself, well inside the slippage-doubling stress of G6. [Assumption] A rule with only one known value has no alternative candidate, so it cannot make a trade outcome-sensitive; it stays flagged in the report. G12 (b) is evaluated only after the Phase 1 market-rule P1 checks have run. A P1 check that cannot resolve a rule leaves its conservative value and its candidates in place; if (b) then exceeds 20%, the verdict is "fails G12: rule-uncertain" and the strategy stays at Level 1. | (a): sizing (shares, from median volume) and the floor (median of daily price × volume, a different statistic from price × median volume) both use c_open, so an order at the floor fills fully on a median-volume day and partly on lower days. A name-level fill rate of about 80–85% at the floor is a reviewer estimate under lognormal volume, not a measurement [Assumption]; 80% therefore binds mainly for names near the floor. (b)–(e): unresolved rules that materially change outcomes, forced exits and an unmeasured auction share each make the result unrepresentative. [Assumption] |

**Verdict text.** The verdict is "passes all gates at VND X per position", or "fails G*n*: ..." listing every failed gate, followed by the family and global trial counts and any labels (`SURVIVORSHIP-BIASED`, `THIN UNIVERSE`). "No strategy passes" is a valid and expected outcome, and it is reported as such.

**Level 2 → 3 and demotion.** These use forward paper monitoring with the same fill and cost model. Checks run at fixed points only, every 20 forward sessions, not daily.
- Level 3 (forward-confirmed) is checked first at ≥ 120 forward sessions and ≥ 20 closed trades. Cumulative forward net excess must lie between the 5th and 95th percentiles of a stationary-bootstrap distribution (S27) of cumulative excess over the same length, built from the H net excess series. It must also be > 0.
- Demotion by one level happens at any check from 60 forward sessions onwards when cumulative forward net excess falls below the 5th percentile of that distribution. The shortlist states the demotion (spec §4).
- The session counts, the check interval and the percentiles are judgement calls. Repeated checks raise the chance of a false demotion, which is the conservative direction. [Assumption]

## Metrics

Conventions apply to every metric:
- **Portfolio.** NAV_0 = K × P, where K = 10 positions and P is the configured grid size (`## Capacity grid`, `## Default risk settings`).
- **Position size.** At each rebalance, the per-position size is P_d = NAV_d ÷ K, so weights start at 1/K and compound with NAV.
- **NAV.** NAV is marked at each session close, net of all costs incurred that session.
- **Returns.** Daily return r_d = NAV_d / NAV_{d−1} − 1. Benchmark daily return b_d is defined in `## Targets and labels`.
- **Annualisation.** A = sessions per year, the average count per calendar year from the verified trading calendar on D dates. Provisionally 250. [Assumption]

Formulas are illustrative, not code.

| Metric | Definition | Misleading when |
|---|---|---|
| CAGR | (NAV_end / NAV_start)^(A / n) − 1, n = sessions | Short samples; it hides path and drawdown; not comparable across periods of different length. |
| Net excess return (annualised) | A × mean(r_d − b_d) | Benchmark choice drives it; survivorship bias inflates both sides only partly. |
| Information ratio (IR) | √A × mean(r_d − b_d) / sd(r_d − b_d) | Overlapping holdings create autocorrelation; also report the Lo (S28) autocorrelation-adjusted value. |
| Sharpe ratio | √A × mean(r_d − rf_d) / sd(r_d − rf_d), with rf = 0 by default | rf = 0 overstates Sharpe when VND deposit rates are positive [Unverified → P1 check: source a VND risk-free series]; √A scaling is wrong under serial correlation (S28); fat tails (covered by DSR, S21). |
| Maximum drawdown | max over d of 1 − NAV_d / max_{s≤d} NAV_s, on daily close NAV; also report duration (sessions from peak to recovery) | One path only; depends heavily on sample length; daily marking understates intraday lows. |
| Turnover (annual, one-way) | (A / n) × Σ_d ½ Σ_i abs(w_i,d^after − w_i,d^before), where w^before = weights drifted from the prior close | It ignores which names are traded; turnover in illiquid names costs more than the number implies. |
| Cost drag | A × mean(daily costs ÷ NAV_{d−1}) | It depends on the cost model being right; for HNX/UPCoM opens it is a proxy. |
| Trade count | Closed round trips; also per year | Many trades in one name or one month inflate it. |
| Exposure | mean over d of (gross long value ÷ NAV_d); also the share of sessions with any position | High excess at low exposure can come from cash timing, not selection. |
| Hit rate, payoff | Share of trades with net return > 0; mean win ÷ mean loss | Meaningless alone; a high hit rate with a small payoff can lose money. |
| Rank IC | Per signal date, the Spearman correlation of score and r_i(t,h); report the mean and a t-statistic over non-overlapping dates | It ignores costs and capacity; a positive IC can coexist with negative net returns. |
| Fill rate | Filled entry shares ÷ intended entry shares | Low values mean the result is not tradable. |
| Forced-exit share | Trades flagged `exit_forced` or `delisted_held` ÷ all trades | High values mean the terminal haircut, not the strategy, drives results. |

**Baseline comparisons.** Every report shows these alongside the strategy:
- the equal-weighted universe benchmark;
- VN-Index buy-and-hold (price return);
- a random-selection baseline: K stocks drawn uniformly from the eligible universe on the same schedule, run 200 times with fixed seeds, reported as a percentile band.

**Uncertainty.** Every headline metric gets a stationary-bootstrap 90% interval (S27, mean block length *h*, 1,000 resamples). The interval level and the resample count are judgement calls. [Assumption]

## Capacity grid

Notional position sizes (VND per position): 20 million, 50 million, 100 million, 200 million, 500 million, 1 billion, 2 billion. Reason: this covers small retail tickets up to sizes where the participation caps bind for mid-cap names. [Assumption]

Which size is the configured default (proposed: VND 100 million) is left to the owner. [Owner decision needed]

For each size P, the full backtest is rerun with NAV_0 = K × P. The liquidity floor scales as P / c_open with the fixed P (`## Universe` item 6), and sizing and fills use the same c_open (`## Execution and fill model` rule 3). Order size P_d = NAV_d ÷ K drifts with NAV. The capacity verdict refers to the starting size P, so the report also gives the maximum and 95th-percentile realised P_d. The report gives per size:
- net excess return, IR, G1/G4/G5/G6/G12 status;
- fill rate;
- median and 95th-percentile participation (filled shares ÷ V_e);
- the share of signals dropped by the liquidity filter;
- the median eligible count.

The verdict states the largest size at which G1, G4, G5, G6 and G12 all pass (G10). Grid reruns are robustness runs, not trials (`## Validation design`).

## Hypothesis backlog

This ranks spec §6's list. No hypothesis is claimed to work; published results below are in-sample findings by their authors.
- "Feasibility" cites data-sources.md `## Scorecard` rows. Every source there is research-only, and history depth is unknown everywhere, so even "high" feasibility is conditional on P1 checks #1–#3.
- The id column gives the only valid `hypothesis_id` values (`## Validation design`). A new id needs a new row here before its first run.

| Id | Rank | Hypothesis | Evidence (Vietnam or similar) | Data feasibility | Notes |
|---|---|---|---|---|---|
| H1 | 1 | Short-term reversal after large moves or limit-down days | HOSE 2004–2021: monthly losers beat winners by 1.80% and 2.17% in months 2–3 [Fact S31]. Vietnamese price limits showed volatility spillover, delayed price discovery and trading interference in a 2003–2006 sample, tested with the Kim & Rhee method [Fact S36]. Kim & Rhee found the same three effects on the Tokyo Stock Exchange [Fact S37]. Cost treatment is not stated in the abstracts read. | High: OHLCV only (VCI, KBS, SSI rows). Needs band-as-of-date for limit-day detection (Market rules "Daily price limit"). | Interacts with the fill model: the model does not block buys at a floor-locked open, but a sell at a later floor lock is unfillable and is retried up to the L cap. |
| H2 | 2 | Market trend filter (when to hold cash) | Time-series momentum in 58 futures and forwards, equity indices included: the past 12-month excess return predicted the future return [Fact S42]. No Vietnam-specific study found. [Assumption] | High: index series from VCI `market-indices` and KBS `index` rows. | An overlay, not a stock selector. Like every strategy it is gated against b_d (G1, G4, G9); VN-Index buy-and-hold is shown for context only. |
| H3 | 3 | Relative strength or momentum versus VN-Index or a sector | Mixed. Short-term momentum persists while medium and long horizons revert in VN-Index stocks 2015–2025 (abstract only, read via search result) [Assumption] (S32). Momentum profits are larger in more individualistic countries [Fact S33]. Whether that implies weak momentum in Vietnam is an inference. [Assumption] | High for VN-Index-relative: OHLCV and index. Sector-relative needs dated sector membership (see H6). | Opposite sign to H1 at similar horizons; test both, but every variant counts as a trial. |
| H4 | 4 | Breakouts confirmed by volume or traded value | US: past volume predicts the size and persistence of momentum, and high-volume winners and low-volume losers reverse faster [Fact S40]. No Vietnam study found. [Assumption] | High: OHLCV. Volume may include put-through (see the fill-model gap table). | Breakouts close to the ceiling are often unfillable at the open; expect a low fill rate. |
| H5 | 5 | Low-volatility (price-based) tilt as a slow baseline | Vietnam 2007–2014: idiosyncratic volatility not priced [Fact S34]. A 2013–2022 student thesis finds high-volatility portfolios outperformed (S43, thesis). [Assumption] The evidence leans against. | High for price-based volatility. Quality tilts need PIT fundamentals: gated on P1 #4 (`## Universe`, fundamentals gate). | Kept as a baseline because it is cheap and low-turnover, not because the evidence supports it. |
| H6 | 6 | Sector rotation | US: industry momentum accounts for much of individual stock momentum [Fact S41]. No Vietnam study found. [Assumption] | Low: ICB codes exist (VCI ICB4, vnstock ICB groups rows) but only as current classification; historical membership unknown. [Unverified → P1 check: dated sector history] | Using today's sectors for past dates is look-ahead; flagged if run. |
| H7 | 7 | Earnings-related drift | PEAD documented in Vietnam, stronger with high insider ownership [Fact S35]. | Gated: no source verified to carry publication dates (data-sources.md `## Four explicit questions`; P1 #4). | Stays at Level 0 until the fundamentals gate passes. |
| H8 | 8 | Foreign or proprietary net flows | Vietnam: net foreign buying associated with market performance, 2020–2022 (abstract via search result) (S38). In banking stocks, abnormal foreign selling depresses prices briefly before reverting, 2006–2023 (abstract via search result) (S39). [Assumption] | Low: no scorecard row verifies a historical foreign-flow series; HNX foreign-trading data is Assumption-tagged (HNX row, S26 in data-sources.md); proprietary flows not seen in any row. [Unverified → P1 check: historical per-ticker foreign and proprietary flows] | Evidence is association or event-study, not out-of-sample prediction. |

Rank order weighs Vietnam-specific published evidence first, then data feasibility. The ordering is itself a judgement call. [Assumption]

## Default risk settings

Each is a proposed default in the single config file (spec §7). Each is recorded in the pre-registration and changed only before freezing.

| Setting | Proposed default | Reason |
|---|---|---|
| Minimum average traded value | `## Universe` item 6: 20-session median daily traded value ≥ max(VND 1 billion, P / c_open), with P the fixed grid size | Scales with position size and the binding fill cap; floor to be replaced by a percentile measured on D dates in Phase 1. [Assumption] |
| Max share of a stock's volume per order | c_open = c_close = q × a = 10% × 2% = 0.2% of daily volume, used for both sizing and fills (`## Execution and fill model` rule 3) | One cap for sizing and filling keeps the fill rate meaningful; a is replaced by the D-date measurement before any held-out run. [Assumption] |
| Position size (P) and NAV | NAV_0 = K × P; per-position order size P_d = NAV_d ÷ K at each buy session (sizing only; eligibility uses P); P = VND 100 million proposed | 100 million is the third of seven grid sizes, a mid-sized retail ticket; NAV-proportional sizing keeps weights at 1/K. [Owner decision needed] |
| Max positions K / max position weight | K = 10 positions; 1/K = 10% of NAV each at entry (drift allowed until exit) | Enough names to diversify single-stock risk while staying manageable for manual order entry. [Assumption] |
| Max sector weight | 30% of NAV by ICB level 1 | Avoids one-sector bets in a bank- and real-estate-heavy market. Sector history is unverified, so the current classification is used and flagged. [Assumption] |
| Portfolio construction | Cycle of h + s sessions (s from `## Execution and fill model` rule 6). Sell session R: using the signal of R − 1, positions not in the top 2K are sold, and positions are held h sessions from entry unless kept. Buy session R + s: using the signal of R + s − 1, free slots are filled from the top K not already held, funded only by settled cash; the next sell session is R + s + h. Run all h + s start offsets as robustness. At the end of D and of every tuning window, no keep decisions are made (`## Validation design`, split rule) | The hold buffer applies the buy/hold spread, which Novy-Marx & Velikov found the most effective cost mitigation [Fact S30]. The signal is always the session before entry, as in the labels. The cash wait follows rule 6; offsets show sensitivity to the start date; the 2K buffer width is a separate judgement call [Assumption]. |
| Stop-loss in backtests | None in the base case. Variants (fixed −8%, or 2 × 20-session ATR from entry) are separate trials. | Stops add parameters and trials. Settlement limits the earliest exit (`## Execution and fill model` rule 5). [Assumption] |
| Invalidation level in reports | 2 × 20-session ATR below the entry price, informational only | Gives the owner a deterministic risk reference without changing the tested rules. [Assumption] |
| Delayed-exit cap L and terminal haircut τ_v | L = 10 sessions; τ_v = 3 × venue band (HOSE 21%, HNX 30%, UPCoM 45%), or 100% if suspended or not traded in the last 5 sessions; τ = 100% sensitivity reported | Bounds every label and position so the purge gap holds (`## Execution and fill model` rule 8). [Assumption] |
| Commission, tax, slippage | As `## Cost model` | Market rules values only. |
| Portfolio drawdown flag | "Risk-off" flag in reports when the paper portfolio's NAV is ≥ 15% below its peak | A report flag only, never an order. 15% is a judgement call. [Assumption] |

## Sources

| Sn | URL | Publisher | Document date | Access date | Notes |
|---|---|---|---|---|---|
| S1 | https://staticfile.hsx.vn/Uploads/UploadDocuments/2453338/HTGD_Quy%20dinh%20can%20biet%20khi%20GDCK%20tren%20HOSE_T2.2026.pdf | HOSE (hsx.vn) | Filename "T2.2026"; PDF metadata 2026-04-15; cites Decision 22/QĐ-HĐTV of 2025-04-18 | 2026-10-27 | Official HOSE investor guide (Vietnamese). Primary for HOSE sessions, bands, tick, lots, order types, status flags, T+2 diagram. |
| S2 | https://luatvietnam.vn/chung-khoan/quyet-dinh-22-qd-hdtv-2025-ban-hanh-quy-che-niem-yet-va-giao-dich-chung-khoan-399805-d1.html | Vietnam Stock Exchange (VNX), Decision 22/QĐ-HĐTV, hosted by luatvietnam.vn | Signed 2025-04-18; takes effect when the new system goes live | 2026-10-27 | Legal text mirror. A later 22/QĐ-HĐTV (2026) that replaces it is listed by thuvienphapluat.vn (HTTP 403, not read); S1 still cites the 2025 text. |
| S3 | https://mbs.com.vn/files/uploads/2025/07/Quy-dinh-giao-dich-chung-khoan-co-so-HSX.22.07.2025.pdf | MB Securities (MBS) | 2025-07-22 (PDF created 2025-07-25) | 2026-10-27 | Broker summary of HOSE rules; secondary. Says T+2 for shares; sell orders need securities held. |
| S4 | https://mbs.com.vn/files/uploads/2025/07/Quy-dinh-giao-dich-chung-khoan-co-so-HNX.22.07.2025.pdf | MB Securities (MBS) | 2025-07-22 | 2026-10-27 | Broker summary of HNX rules; secondary. |
| S5 | https://mbs.com.vn/files/uploads/2025/07/Quy-dinh-giao-dich-chung-khoan-co-so-UPCOM.22.07.2025.pdf | MB Securities (MBS) | 2025-07-22 | 2026-10-27 | Broker summary of UPCoM rules; secondary and the only UPCoM source read. |
| S6 | https://tuoitre.vn/nld/krx-system-officially-goes-live-19625050517142482.htm | Tuoi Tre | 2025-05-05 | 2026-10-27 | News report of the KRX go-live and rule changes on 2025-05-05. |
| S7 | https://doanhnghiephoinhap.vn/hose-sap-thay-doi-quy-dinh-giao-dich-98076.html | Doanh nghiep & Hoi nhap | 2025-03-13 | 2026-10-27 | News report of HOSE's announced rule changes for the new system; describes pre-KRX rules as "currently". |
| S8 | https://www.sggp.org.vn/ngay-29-8-se-chinh-thuc-rut-ngan-thoi-gian-giao-dich-chung-khoan-som-1-ngay-t2-post648215.html | Sai Gon Giai Phong | 2022-08-19 | 2026-10-27 | News report of VSD Decisions 109/QĐ-VSD and 110/QĐ-VSD effective 2022-08-29 (T+3 to T+2). VSD decision texts not read. |
| S9 | https://vnbusiness.vn/tu-41-hose-chinh-thuc-dieu-chinh-lo-giao-dich-toi-thieu-len-100-co-phieu.html | VnBusiness | 2020-12-31 | 2026-10-27 | News report: HOSE lot size 10 to 100 from 2021-01-04. |
| S10 | https://cms.luatvietnam.vn/uploaded/Others/2025/12/30/Luat-109-2025-QH15_3012143156.pdf | National Assembly of Vietnam, Law 109/2025/QH15 (Personal Income Tax), hosted by luatvietnam.vn | Adopted 2025-12-10; effective 2026-07-01 (Art. 29) | 2026-10-27 | Legal text read with pdftotext. Arts. 3(3)(b), 12(1), 13(2), 29. |
| S11 | https://luatvietnam.vn/tin-van-ban-moi/muc-gia-dich-vu-trong-linh-vuc-chung-khoan-tai-so-giao-dich-chung-khoan-viet-nam-186-101997-article.html | luatvietnam.vn (news summary of Ministry of Finance Decision 1541/QĐ-BTC) | 2025-04-29 | 2026-10-27 | Secondary summary. Fee table in the Decision not read directly. |
| S12 | https://doanhnghiephoinhap.vn/bieu-muc-gia-dich-vu-moi-va-chi-tiet-cho-linh-vuc-chung-khoan-103133.html | Doanh nghiep & Hoi nhap | 2025-05-05 | 2026-10-27 | News summary of the same schedule: 0.027% HNX/HOSE, 0.018% UPCoM, custody 0.27 VND per unit per month. |
| S13 | https://www.ssi.com.vn/khach-hang-ca-nhan/bieu-phi/bieu-gia-dich-vu-giao-dich-chu-dong | SSI Securities | Effective 2025-10-10 | 2026-10-27 | Broker fee page. Fetched table tiers for staff channel were ambiguous; range given conservatively. |
| S14 | https://www.dsc.com.vn/bieu-phi/bieu-phi-giao-dich-chung-khoan-niem-yet | DSC Securities | Effective 2025-08-20 | 2026-10-27 | Broker fee page. Does not say whether exchange fees are included. |
| S15 | https://www.kbsec.com.vn/pic/general/files/18_%20VN_Bi%E1%BB%83u%20ph%C3%AD%20d%E1%BB%8Bch%20v%E1%BB%A5%20t%E1%BB%AB%2022_07_2026.pdf | KB Securities Vietnam (KBSV) | Effective 2026-07-22 | 2026-10-27 | Broker fee schedule PDF, read with pdftotext. |
| S16 | https://images.vps.com.vn/2025/files/bieu-phi-chung-khoan-niem-yet-cb2a.pdf | VPS Securities | Effective 2025-07-01 | 2026-10-27 | Broker fee schedule PDF; states fees include exchange and VSDC fees per Circular 101/2021/TT-BTC. |
| S17 | https://thitruongtaichinhtiente.vn/lich-nghi-giao-dich-chung-khoan-tet-nguyen-dan-binh-ngo-2026-77799.html | Thi truong Tai chinh Tien te | 2026-02-13 | 2026-10-27 | News report of HOSE and HNX Tết 2026 closure and settlement dates. |
| S18 | https://hrspring.vn/wp-content/uploads/2026/07/Van-ban-hop-nhat-112-VBHN-VPQH.pdf | National Assembly Office, consolidated text 112/VBHN-VPQH of the Personal Income Tax Law, hosted by hrspring.vn | Consolidated 2026 (date not shown in readable text) | 2026-10-27 | Confirms Law 109/2025/QH15 of 2025-12-10, effective 2026-07-01, amended by Law 09/2026/QH16 of 2026-04-24. Only the first pages were text-readable. |
| S19 | https://luatvietnam.vn/chung-khoan/quyet-dinh-109-qd-vsd-trung-tam-luu-ky-chung-khoan-228448-d1.html | Vietnam Securities Depository (VSD), Decision 109/QĐ-VSD, hosted by luatvietnam.vn | 2022-08-19; effective 2022-08-29 | 2026-10-27 | Page shows dates and that it replaces Decision 211/QĐ-VSD and is itself shown as replaced by Decision 15/QĐ-HĐTV (2023). Operative articles not readable. |
| S20 | https://vneconomy.vn/bien-dong-gia-chung-khoan-tren-upcom-chinh-thuc-len-toi-15.htm | VnEconomy | 2017-06-21 | 2026-10-27 | News: UPCoM ±15% band decision effective 2017-06-20, replacing Decision 79/QĐ-SGDHN of 2016-02-05. Supports an Assumption only. |
| S21 | https://www.davidhbailey.com/dhbpapers/deflated-sharpe.pdf | Bailey, D. H. and López de Prado, M., "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality", Journal of Portfolio Management 40(5), 94-107, DOI 10.3905/jpm.2014.40.5.094 | 2014 (author copy dated 2014-07-31) | 2026-10-28 | Author copy fetched; title page confirms title, authors and "Journal of Portfolio Management, Forthcoming, 2014". Volume, pages and DOI from the publisher DOI record (fetch redirected to pm-research.com, HTTP 403). Method source for G1. |
| S22 | https://escholarship.org/uc/item/4w1110bb | Bailey, D. H., Borwein, J. M., López de Prado, M. and Zhu, Q. J., "The Probability of Backtest Overfitting", Journal of Computational Finance 20(4), DOI 10.21314/jcf.2016.322 | 2017 | 2026-10-28 | eScholarship PDF fetched; cover page confirms journal, volume, year, DOI and authors (CC BY-NC 4.0). Method source for PBO/CSCV (G3). |
| S23 | https://www.econometricsociety.org/publications/econometrica/2000/09/01/reality-check-data-snooping | White, H., "A Reality Check for Data Snooping", Econometrica 68(5), 1097-1126 | 2000-09 | 2026-10-27 | Publisher record seen via search result. |
| S24 | https://ideas.repec.org/a/bes/jnlbes/v23y2005p365-380.html | Hansen, P. R., "A Test for Superior Predictive Ability", Journal of Business & Economic Statistics 23, 365-380 | 2005-10 | 2026-10-27 | RePEc record fetched (no abstract on page). Method source for G2. |
| S25 | https://www.nber.org/papers/w20592 | Harvey, C. R., Liu, Y. and Zhu, H., "...and the Cross-Section of Expected Returns", Review of Financial Studies 29(1), 5-68 (NBER WP 20592) | 2016 (WP 2014) | 2026-10-27 | Seen via search result; argues t > 3.0 hurdle under multiple testing. |
| S26 | https://libcat.scu.edu/Record/b3136103/Details | López de Prado, M., Advances in Financial Machine Learning, Wiley, Hoboken NJ | 2018 | 2026-10-27 | Library record only; purging/embargo described via secondary pages, so the purge rule here is this document's design, not a quote. |
| S27 | https://gnosis.library.ucy.ac.cy/handle/7/57533 | Politis, D. N. and Romano, J. P., "The Stationary Bootstrap", Journal of the American Statistical Association 89(428), 1303-1313 | 1994 | 2026-10-27 | Library record seen via search result. |
| S28 | https://rpc.cfainstitute.org/research/financial-analysts-journal/2002/the-statistics-of-sharpe-ratios | Lo, A. W., "The Statistics of Sharpe Ratios", Financial Analysts Journal 58(4) | 2002-07 | 2026-10-27 | CFA Institute record seen via search result: monthly Sharpe cannot generally be annualised by √12. |
| S29 | https://projects.nber.org/confer/2009/mms09/Corwin_Schultz.pdf | Corwin, S. A. and Schultz, P., "A Simple Way to Estimate Bid-Ask Spreads from Daily High and Low Prices", Journal of Finance 67(2), 719-759 (working-paper copy) | 2012 (WP 2009) | 2026-10-27 | Seen via search result. Spread proxy in the cost model. |
| S30 | https://ideas.repec.org/a/oup/rfinst/v29y2016i1p104-147..html | Novy-Marx, R. and Velikov, M., "A Taxonomy of Anomalies and Their Trading Costs", Review of Financial Studies 29(1), 104-147 | 2016 | 2026-10-28 | RePEc record and abstract fetched: a buy/hold spread is the most effective cost mitigation; trading costs always reduce strategy profits. US data. |
| S31 | https://ideas.repec.org/a/gam/jijfss/v11y2023i2p58-d1110999.html | Truong, L. D., Cao, G. N., Friday, H. S. and Doan, N. T., "Overreaction in a Frontier Market: Evidence from the Ho Chi Minh Stock Exchange", International Journal of Financial Studies 11(2) | 2023-03 | 2026-10-27 | RePEc record and abstract fetched; 392 HOSE stocks, 2004-2021, monthly; costs not mentioned. |
| S32 | https://businessperspectives.org/journals/investment-management-and-financial-innovations/issue-509/an-integrated-momentum-strategy-based-on-entropy-and-behavioral-overreaction-evidence-from-vietnam | Vu, L. T., Nguyen, M. P. and Hoang, Q. A., Investment Management and Financial Innovations 23(1), 154-171, DOI 10.21511/imfi.23(1).2026.12 | 2026 | 2026-10-27 | Page returned HTTP 403; abstract seen via search result only, so Assumption. Reports an in-sample backtest Sharpe, not relied on. |
| S33 | https://ideas.repec.org/a/bla/jfinan/v65y2010i1p361-392.html | Chui, A. C. W., Titman, S. and Wei, K. C. J., "Individualism and Momentum around the World", Journal of Finance 65(1), 361-392 | 2010-02 | 2026-10-27 | RePEc record and abstract fetched. |
| S34 | https://ideas.repec.org/a/mes/emfitr/v53y2017i4p746-763.html | Fang, K., Wu, J. and Nguyen, C., "The Risk-Return Trade-Off in a Liberalized Emerging Stock Market: Evidence from Vietnam", Emerging Markets Finance and Trade 53(4), 746-763 | 2017 | 2026-10-27 | RePEc record and abstract fetched; 2007-2014. |
| S35 | https://ideas.repec.org/a/eee/riibaf/v70y2024ipbs0275531924001454.html | Ho, T. Q., Nguyen, Y. and Tran, H., "The impact of insider ownership and institutional ownership on post-earnings-announcement-drift: Evidence from Vietnam", Research in International Business and Finance 70(PB) | 2024 | 2026-10-27 | RePEc record and abstract fetched; sample period not shown. |
| S36 | https://ideas.repec.org/p/osf/osfxxx/6ru75.html | Tran, V. H., "Price limit regulation and herd behavior in the Vietnamese stock market", OSF Preprints | 2007 | 2026-10-27 | RePEc record and abstract fetched; 2003-2006, preprint. |
| S37 | https://ideas.repec.org/a/bla/jfinan/v52y1997i2p885-99.html | Kim, K. A. and Rhee, S. G., "Price Limit Performance: Evidence from the Tokyo Stock Exchange", Journal of Finance 52(2), 885-899 | 1997-06 | 2026-10-28 | RePEc record and abstract fetched: evidence supports the volatility-spillover, delayed-price-discovery and trading-interference hypotheses. |
| S38 | https://hvtc.edu.vn/tabid/1631/baibao/285/title/impact-of-foreign-investors-on-the-vietnamese-stock-market-in-new-context/Default.aspx | Hoang, A. T. and Le, T. N., Journal of Finance & Accounting Research (Academy of Finance) | 2025 | 2026-10-27 | Page returned HTTP 404 on fetch; abstract seen via search result only, so Assumption. |
| S39 | https://publisher.unimas.my/ojs/index.php/IJBS/article/view/9543 | Dang, Le and Trinh, "The Impact of Foreign Investors' Abnormal Trading on the Abnormal Returns of Banking Sector Stocks: The Case of Vietnam", International Journal of Business and Society 26(1) | 2025 | 2026-10-27 | Fetch refused (connection); abstract seen via search result only, so Assumption. |
| S40 | https://ideas.repec.org/a/bla/jfinan/v55y2000i5p2017-2069.html | Lee, C. M. C. and Swaminathan, B., "Price Momentum and Trading Volume", Journal of Finance 55(5), 2017-2069, DOI 10.1111/0022-1082.00280 | 2000-10 | 2026-10-28 | RePEc record and abstract fetched. US data. |
| S41 | https://ideas.repec.org/a/bla/jfinan/v54y1999i4p1249-1290.html | Moskowitz, T. J. and Grinblatt, M., "Do Industries Explain Momentum?", Journal of Finance 54(4), 1249-1290 | 1999-08 | 2026-10-28 | RePEc record and abstract fetched. US data. |
| S42 | https://www.aqr.com/library/journal-articles/time-series-momentum | Moskowitz, T. J., Ooi, Y. H. and Pedersen, L. H., "Time Series Momentum", Journal of Financial Economics | 2012 (page dated 2012-05-01) | 2026-10-28 | AQR library page and abstract fetched: 58 futures/forwards incl. equity indices; trailing 12-month return predicts future return. Volume/pages not on the page (SSRN 2089463 returned HTTP 403). Not Vietnamese equities. |
| S43 | https://lutpub.lut.fi/handle/10024/165935 | LUT University (bachelor's thesis), "Low volatility anomaly in Vietnam's stock market" | not shown | 2026-10-27 | Student thesis seen via search result; supports Assumption only. |
