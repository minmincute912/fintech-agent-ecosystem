# M2 design: Vietnamese fundamentals and news for the agent team

Status: approved by owner 2026-11-24. Builds on M1 (merged at 78b1fa4) and the
source survey `docs/research/m2-vn-sources.md`.

## Intent

The owner uses the platform to support manual swing-trade entries (5–20 sessions) on
HOSE/HNX/UPCoM. In M1 the agents see prices only, so the bull/bear debate argues from the
model's own memory of the company (seen in the VNM report of 2026-11-24). M2 gives the
fundamentals and news analysts real Vietnamese data, dated so that an analysis on date D
never sees anything published after D.

## Goals

1. `vsi analyze T --date D` runs the market, fundamentals and news analysts.
2. Fundamentals analyst gets quarterly and annual income statement, balance sheet and cash
   flow for T, plus a compact summary, from statements whose availability date is ≤ D.
3. News analyst gets Vietnamese news about T (company news) and market-wide Vietnamese
   business news, published ≤ D, within the window the agent asks for.
4. Tools with no Vietnamese source (US macro from FRED, Polymarket, insider transactions)
   return an explicit "not available for Vietnam" result instead of US data.
5. Every number in the fundamentals tool output comes straight from the source; nothing is
   computed by the LLM.
6. Measured cost per run with three analysts, recorded like M1.

## Non-goals

- Official exchange disclosures (HOSE/HNX/SSC/VSDC): not machine-readable today (survey §1).
- Insider transactions, foreign-flow data, macro data for Vietnam.
- Telegram, scheduling on a VPS (M3+). A daily news-collect command is in scope; running it
  on a timer is not.
- Translating news, summarising full article bodies, or fetching article pages: RSS title and
  description only.
- Point-in-time correctness proven across all history (see Constraints, createdDate).

## Anti-goals (failure even if it "works")

- A fundamentals figure that differs from the source, or a statement used before its
  availability date (look-ahead).
- US macro or US news presented as relevant to a Vietnamese stock.
- News text able to make the agent do anything other than read (prompt injection); agents
  have read-only tools, and news text is marked as untrusted quoted content.
- Republishing news content (outlets allow free reading by individuals, not republishing).

## Constraints

- **Fundamentals source (owner decision 2026-11-24, option A):** VNDirect finfo,
  `https://api-finfo.vndirect.com.vn/v4/financial_statements` and `/v4/financial_models`
  (item names, Vietnamese and English). Undocumented, no key, terms not readable (403).
  Labelled **research-only, personal use**. If it breaks, the tools return
  `DATA_UNAVAILABLE`; nothing falls back to another undocumented source silently.
- **Availability date:** a statement period is available on D only if its `createdDate` ≤ D.
  `createdDate` as publication date is an **Assumption**: probe 2026-11-24 shows VNM Q3 2026
  created 2026-10-30. M2 must check it against known publication dates (Task gate below).
- **News sources (free for individuals per their RSS pages):** VnExpress `kinh-doanh`,
  VnEconomy `chung-khoan` and `nhip-cau-doanh-nghiep`, Báo Đầu tư `kinh-doanh` and
  `thong-tin-doanh-nghiep`, Tuổi Trẻ `kinh-doanh`, CafeF `thi-truong-chung-khoan` and
  `doanh-nghiep`, Vietstock `co-phieu`. Exact feed URLs are in the survey §5. Attribution
  (outlet name + link) is kept with every item.
- **News history:** feeds hold only recent items. A local store keeps items so that a window
  of 7 days exists. Analyses for dates before the store started get fewer or no items; the
  tool says so rather than pretending coverage.
- **Storage:** news items (title, description, link, outlet, pubDate, fetched_at) and nothing
  else, in a local SQLite file under the TradingAgents home (`~/.tradingagents/vsi/`).
  Fundamentals are not stored on disk (in-process cache only, like M1 prices).
- TradingAgents stays a pinned, unmodified dependency; new data enters through the vendor
  router and `vsi.bridge.install()`, each redirected name with a test (same rule as M1).
- No new dependencies unless the standard library cannot do it (RSS is XML: `xml.etree`).
- Secrets: none new.

## Approaches considered

| Approach | Trade-off | Decision |
|---|---|---|
| A. VNDirect finfo for statements, RSS for news | Free, works today; undocumented, terms unread, `createdDate` unproven | **Chosen by owner 2026-11-24** |
| B. Paid feed (Vietstock DataFeed / FiinGroup) | Contracted, documented; quote-only price, slower start | Fallback if A breaks or fails the gate |
| C. No fundamentals, news only | Zero risk; agents keep arguing fundamentals from memory | Rejected |
| News via per-ticker pages (CafeF/Vietstock) instead of RSS | Ticker-specific; script-rendered or dates without times, scraping | Rejected |

## Design

### Components (all in `vsi/`)

- `finfo.py` — client for VNDirect finfo: statements for a ticker and report type, item
  names (cached per process). Raises TradingAgents' vendor error types like `dnse.py`.
- `fundamentals.py` — router vendor functions `get_fundamentals`, `get_balance_sheet`,
  `get_cashflow`, `get_income_statement` with TradingAgents' signatures. Each filters to
  periods with `createdDate` ≤ D, keeps the latest 4 quarters or 4 years, and renders a
  compact table: item name (Vietnamese + English), one column per period, values in VND as
  given, header with source, availability rule and the research-only label.
  `get_fundamentals` returns a short summary computed by code, per layout, each figure with
  its period and `createdDate`, plus quarter-on-quarter and year-on-year change:
  non-financial: revenue, gross profit, net profit, total assets, equity, operating cash
  flow; bank: net interest income, non-interest income, operating expenses, credit-loss
  provisions, net profit, total assets, customer loans, customer deposits, equity;
  securities: operating revenue by main line where the layout has it, net profit, total
  assets, margin lending if itemised, equity; insurance: net premium revenue, net profit,
  total assets, equity. The layout is detected from the finfo model/note of the ticker.
  Each layout's item mapping is tested against one published report (figures typed into a
  test fixture from the company's published statement, with its source cited).
- `news.py` — RSS fetch and parse (stdlib), the SQLite store, `collect()` (fetch all feeds,
  insert new items by link), and router vendor functions `get_news` (company) and
  `get_global_news` (market-wide). Company match: ticker as a whole word (e.g. `VNM`,
  `VNM:`), or the DNSE `shortName`/`name` in title or description. Items with
  pubDate ≤ D (Vietnam time) and ≥ start date. Output lists outlet, time, title,
  description, link; the block is fenced and introduced as untrusted third-party text.
  Before reading, `get_news`/`get_global_news` call `collect()` at most once per process so a
  fresh run has today's items.
- `unavailable.py` (or inside `bridge.py`) — vendor functions for `get_insider_transactions`,
  `get_macro_indicators`, `get_prediction_markets` that raise `VendorUnavailableError("no
  Vietnamese source for …")`, so the router answers `DATA_UNAVAILABLE`.
- `markets.py` — `VN_ANALYSTS = ("market", "fundamentals", "news")`; `vn_config()` points
  `fundamental_data` and `news_data` at the new vendors, and `macro_data`/
  `prediction_markets` at the unavailable vendor.
- `bridge.install()` — registers the new vendor functions. If TradingAgents reaches any
  fundamentals/news path outside the router (as M1 found for prices), patch it the same way,
  with a test. The builder must check this, as M1 did for Yahoo.
- `cli.py` — new command `vsi collect-news` (one fetch of all feeds into the store; prints
  counts per outlet; exit 1 if every feed failed). `vsi analyze` unchanged apart from the
  analyst set.

### Data flow

```
vsi collect-news (manual now, timer later) ──► RSS feeds ──► ~/.tradingagents/vsi/news.sqlite
vsi analyze T --date D
  ├─ market analyst ──────── DNSE (M1)
  ├─ fundamentals analyst ── finfo statements, createdDate ≤ D
  └─ news analyst ────────── news.sqlite (+ one collect), pubDate ≤ D
                             macro / prediction markets / insider → DATA_UNAVAILABLE
```

### Errors

finfo down or changed shape → `VendorUnavailableError` → `DATA_UNAVAILABLE` in the tool
output; the run continues. A ticker with no statements → `NoMarketDataError`. One feed down
during collect → logged and skipped; others continue.

## Gates and checks

1. **createdDate gate (before wiring into analysis):** probe 5 tickers across HOSE/HNX/UPCoM
   for the last 4 quarters and compare `createdDate` with the publication date shown by a
   second public source (company IR page or an exchange/CafeF disclosure item). Record in
   `docs/research/finfo-probe.md`. STOP and report if `createdDate` is earlier than
   publication for any sample (that would be look-ahead), or if it is later by more than
   ~10 days on most samples (data would be stale; owner decides).
2. **Look-ahead tests:** statements created after D are excluded; news published after D is
   excluded; boundary at D in Vietnam time.
3. **Live run:** four runs on the last full session: VNM (HOSE, non-financial), VCB (bank),
   SHS (HNX, securities), and one UPCoM ticker;
   check cited revenue/profit equal finfo; news items cited exist in the store with
   pubDate ≤ D; record tokens and cost in `docs/research/m2-run-cost.md`.

## Calls made by the designer (owner may override)

- **Restated figures:** finfo holds current values only, so a period restated after D shows
  the restated numbers (a look-ahead the date filter cannot remove). The finfo probe records
  `modifiedDate` against `createdDate` for every sample. The tool header always says "values
  as currently held by the source; may include later restatements", and periods whose
  `modifiedDate` > D are marked "revised after analysis date". If most samples are modified
  after creation, the gate stops and the owner decides.
- **Second source for the createdDate gate:** Vietstock per-ticker news
  (`finance.vietstock.vn/{T}/tin-moi-nhat.htm`, readable without script; it lists dated
  "BCTC"/"CBTT" items) or the company's IR page. Date granularity is enough. If neither is
  reachable for a sample, that sample goes to the owner for a manual check; the plan has an
  owner hand-off step.
- **Order:** the news half (RSS, store, `collect-news`, news tools, the unavailable stubs) does
  not depend on finfo and is built and testable first. Fundamentals are wired into analysis
  only after the gate passes. If the gate fails, news can still merge alone, with the owner's
  approval.

## Decided by the owner

- Fundamentals source A (VNDirect finfo), research-only (2026-11-24).
- News via free RSS of Vietnamese outlets (proposal accepted with A).
- Milestone order unchanged; M2 approved to start (2026-11-24).
- Banks, securities firms and insurers (2026-11-24, full support): statement tables in the
  source's own layout for every ticker, and a code-computed `get_fundamentals` summary for all
  four layouts: non-financial (TT200), bank (TT49), securities (TT334), insurance (TT199/232).
  The LLM computes nothing. Sector summaries use only items in the three main statements;
  notes-based metrics (NPL, CASA, CAR) are out of scope because finfo has no notes.

## Left to the builder

- Exact finfo query parameters (`modelType` per statement, report types), item-name mapping
  and which items appear in the compact tables.
- SQLite schema details, de-duplication key, retention.
- Word-boundary matching rules and their tests; handling of feeds with odd dates.
- Whether `get_global_news` uses only market feeds or all feeds.
- Output formatting, as long as sources, dates and the research-only label are shown.
