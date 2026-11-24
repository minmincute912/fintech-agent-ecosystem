# M2 source survey: Vietnamese fundamentals and news

Surveyed 2026-11-24 for M2 (VN fundamentals with publication dates, Vietnamese news).
Pages were read with a fetch tool or `curl` from the owner's machine; forum and GitHub
evidence came from web search. "Not stated" = the page read is silent. Nothing here was
signed up for or paid for. Builds on `data-sources.md` (Phase 0) and its DNSE update.

## 1. Official sources (exchanges, regulator, depository)

| Source | What | Automated access from here | Terms |
|---|---|---|---|
| HOSE hsx.vn | Disclosures ("Tin công bố thông tin") | Home page 200 but content is JS-rendered; `/vi/tin-tuc` timed out | Not found |
| HNX hnx.vn | Disclosures, daily trading data downloads | TLS certificate chain fails (curl error 60, fetch "unable to verify the first certificate") | Not read |
| SSC ssc.gov.vn, IDS (ids/congbothongtin.ssc.gov.vn) | Filings, financial-statement PDFs | ssc.gov.vn redirect loop; IDS hostnames do not resolve | Not read |
| VSDC vsd.vn / vsdc.com.vn | Record-date notices | vsd.vn cert mismatch (cert is for vsdc.vn); vsdc.com.vn timed out | Not read |

Finding: official disclosures cannot be read automatically today without reverse-engineering
JS pages or ignoring TLS errors. Not usable for M2.

## 2. Brokers

| Source | Fundamentals | News | Notes |
|---|---|---|---|
| DNSE OpenAPI (in use) | No statements endpoint in spec 2026-09-15 | No | Corporate-action history only per own account |
| VNDirect finfo `api-finfo.vndirect.com.vn/v4/financial_statements` | Yes: quarterly/annual items, no key. Probe 2026-11-24: VNM Q3 2026 (`fiscalDate` 2026-09-30) rows carry `createdDate` 2026-10-30, 15,747 rows total | No | Undocumented; vndirect.com.vn terms returned 403, not read. `createdDate` may approximate publication date `[Assumption]`; a restatement or reload could change it |
| TCBS `apipubaws.tcbs.com.vn` | Used by old vnstock | — | 403 from fetch tool; terms not read |
| Vietcap (VCI) / KBS | Used by vnstock 4.x | KBS has a news endpoint | Phase 0: VCI terms bar copying/commercial use; KBS terms not found |
| SSI FastConnect | Spec PDF mentions fundamental data | — | Dropped in M1 (counter sign-up, fixed IP) |
| Finhay, BSC | Not assessed / partner-only | — | See data-sources.md DNSE update |

## 3. Data vendors

| Vendor | Statements | Publication date | Price | Terms for automated personal use |
|---|---|---|---|---|
| Vietstock DataFeed / VietstockXLS | Yes, ">136,000 báo cáo tài chính chuẩn hóa", API or sync | Not stated | Quote only (kinhdoanh@vietstock.vn); targets companies | Not stated |
| VietstockFinance web | Statements viewable, PDF/Excel export on paid tiers | Per-ticker news shows dates, not times | Package page lists courses, not data prices | Not stated |
| FiinGroup API DataFeed | Yes, "chi tiết tới thuyết minh", audit opinions | Not stated | Quote only | Terms PDF is scanned; not readable without OCR |
| FiinQuant | Python library on Fiin data | Not stated | Tiered VND/month; online sign-up "tạm ngừng" | Not read |
| Simplize | Web: 2 years free, unlimited on Professional | Not stated | 599k VNĐ/month or 5,988k VNĐ/year | Terms forbid copying/distribution/derivatives without consent; no API stated |
| FireAnt | Ratios in MetaKit for AmiBroker | Not stated | 1.429k–5.750k VNĐ/year memberships | No API/automation terms found |
| DataCore | Not stated (sample datasets: prices, GDP) | Not stated | Demo free, paid with key | docs.datacore.vn did not resolve |
| iTick | `/stock/info` for Vietnam (P/E, market cap); no statement endpoint | News has publish time; VN coverage not stated | Free "personal use only" 5 calls/min; $79+/month | Bars scripts/crawlers without written consent |
| EODHD | Claims VN fundamentals | Not verified | Not read (pages failed to load) | Phase 0: storage allowed for non-professional users |
| XNO | Web platform (free); `xnoapi` library | Not stated | Platform free | Not stated |

## 4. Open-source libraries (wrap the sources above; none is a data source itself)

| Library | Upstream for statements | Notes |
|---|---|---|
| vnstock (Gen 5) | VCI, KBS, TCBS; new `vnstock-oapi` uses the user's broker Open API key | PyPI 4.0.8 quarantined (Phase 0); licence defers to each source's terms |
| vnfin (Apache-2.0) | VNDirect finfo → CafeF Ajax | "Fetched data is for personal/internal research"; no publication date exposed |
| vnquant | VNDirect, CafeF | No licence file |
| vietfin (Apache-2.0) | "public APIs from multiple brokerage firms" | Income + events shown |
| xnoapi, quantvn | Need API key | PyPI page blocked by a challenge |

## 5. News

| Outlet | RSS | Terms on RSS / reuse |
|---|---|---|
| VnExpress | `vnexpress.net/rss/kinh-doanh.rss` | "miễn phí cho các cá nhân và các tổ chức phi lợi nhuận"; commercial copying needs written approval |
| VnEconomy | `vneconomy.vn/chung-khoan.rss`, `tai-chinh.rss`, `nhip-cau-doanh-nghiep.rss` … | Same free-for-individuals wording; republishing needs written approval |
| Báo Đầu tư | `baodautu.vn/kinh-doanh.rss`, `thong-tin-doanh-nghiep.rss` … | Same free-for-individuals wording; use of content needs written approval |
| Tuổi Trẻ | `tuoitre.vn/kinh-doanh.rss` | Same free-for-individuals wording |
| Thanh Niên | `thanhnien.vn/rss/kinh-te/chung-khoan.rss`, `kinh-te/doanh-nghiep.rss` | Attribution on reuse; footer also bars copying without written approval |
| CafeF | `cafef.vn/thi-truong-chung-khoan.rss`, `doanh-nghiep.rss` … | Attribution "Theo cafef"; terms page 404 |
| Vietstock | `vietstock.vn/830/chung-khoan/co-phieu.rss` … | No terms on RSS page |
| Stockbiz | `stockbiz.vn/api/rss/*.rss` (30 items, aggregator) | "chỉ dùng cho mục đích đọc tin cá nhân" |
| Tin nhanh chứng khoán, Nhịp Cầu Đầu Tư, NDH, VietnamFinance, VIR, 24hmoney | No RSS found | Reuse needs attribution or written approval |

Per-ticker disclosure lists (CafeF event pages, Vietstock `/{T}/tin-moi-nhat.htm`) exist, but
CafeF loads them by script, and Vietstock shows dates without times.

## 6. Forums and community

- F319: data threads are about AmiBroker price feeds (DNSE Ami X free history, FireAnt MetaKit,
  paid ift/profindat/datapro). No thread found on automated financial-statement feeds.
- Voz, Tinhte, Reddit: searches returned no relevant threads.
- GitHub: the community relies on undocumented broker endpoints (VNDirect, TCBS, VCI, KBS,
  CafeF) through vnstock/vnfin/vnquant, and warns they break and are for personal research.

## Conclusions

1. **News: solvable now, free.** RSS from VnExpress, VnEconomy, Báo Đầu tư, Tuổi Trẻ, CafeF,
   Vietstock gives timestamped items (`pubDate`). The terms allow free use by individuals; the
   outlets restrict republishing, not reading. Feeds hold only recent items, so a 7-day window
   needs a local daily store.
2. **Fundamentals: no source is both documented and terms-clear.** Options:
   - Paid, documented: Vietstock DataFeed, FiinGroup API (quote only), EODHD (unverified for VN).
   - Free, undocumented: VNDirect finfo (works today, has `createdDate`), CafeF Ajax. Personal
     research only, may break, terms unread.
3. **Official disclosures (HOSE/HNX/SSC/VSDC): not machine-readable from here.**

## Not checked

VNDirect, TCBS and Vietcap terms (403 or not found); EODHD and Vietstock DataFeed prices;
FiinGroup terms (scanned PDF); whether VNDirect `createdDate` equals the publication date
(needs comparison with known publication dates for several tickers).
