"""Vietnamese Telegram summary of one analysis, with code-checked agent price levels.

Data lines come from DNSE, finfo and the news store. Agent text is quoted under its own heading,
marked unchecked (owner decision 2026-11-25, option d). Prices are thousand VND, as DNSE gives them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

# Daily price limits (docs/quant-methodology.md "Daily price limit", current rules)
BANDS = {"HOSE": 0.07, "HNX": 0.10, "UPCOM": 0.15}
_FIELD = re.compile(r"^\*\*([^*]+)\*\*:\s?(.*)$")
_LABELS = {"entry": "Vào lệnh", "stop": "Cắt lỗ", "target": "Mục tiêu"}
# UPCoM reference price is the prior session's VWAP (quant-methodology.md), not the close
_ESTIMATED_REFERENCE = " (tham chiếu ước tính bằng giá đóng cửa; giá tham chiếu thật là bình quân gia quyền phiên trước)"


@dataclass
class MarketFacts:
    exchange: str
    last_bar: date
    close: float
    low60: float
    high60: float


def parse_fields(markdown: str) -> dict[str, str]:
    """`**Name**: value` blocks as TradingAgents renders them; a value runs until the next field."""
    fields: dict[str, list[str]] = {}
    current = None
    for line in markdown.splitlines():
        m = _FIELD.match(line.strip())
        if m:
            current = m.group(1).strip()
            fields[current] = [m.group(2)]
        elif current and line.strip() and not line.startswith("FINAL TRANSACTION PROPOSAL"):
            fields[current].append(line.strip())
    return {k: "\n".join(v).strip() for k, v in fields.items()}


def vn_num(x: float, decimals: int = 2) -> str:
    """52.3 -> '52,30'; 2126000 -> '2.126.000' (Vietnamese separators)."""
    return f"{x:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


def _price(value: str | None) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None  # "not provided" or free text: not a level


def check_levels(levels: dict[str, float | None], close: float, low60: float, high60: float,
                 band: float) -> tuple[dict[str, float], list[str]]:
    """Entry within the next session's band; stop and target within the 60-session range widened by one band."""
    kept, notes = {}, []
    for key, value in levels.items():
        if value is None or value <= 0:
            continue
        if key == "entry":
            lo, hi, where = close * (1 - band), close * (1 + band), "biên độ phiên tới"
        else:
            lo, hi, where = low60 * (1 - band), high60 * (1 + band), "vùng giá 60 phiên (nới một biên độ)"
        if lo <= value <= hi:
            kept[key] = value
        else:
            # the failing value itself is never shown as a number (spec anti-goal)
            notes.append(f"Bỏ mức {_LABELS[key].lower()} agent đưa ra: nằm ngoài {where} {vn_num(lo)} – {vn_num(hi)}")
    return kept, notes


def _d(day: date) -> str:
    return f"{day:%d/%m/%Y}"


def build_summary(ticker: str, analysis_date: str, facts: MarketFacts, quarter: tuple[date, date] | None,
                  news_since: date | None, decision_md: str, trader_md: str) -> str:
    decision, trader = parse_fields(decision_md), parse_fields(trader_md)
    band = BANDS.get(facts.exchange.upper(), BANDS["UPCOM"])
    levels = {"entry": _price(trader.get("Entry Price")), "stop": _price(trader.get("Stop Loss")),
              "target": _price(decision.get("Price Target"))}
    kept, notes = check_levels(levels, facts.close, facts.low60, facts.high60, band)
    statements = f"BCTC quý {_d(quarter[0])} (tạo {_d(quarter[1])})" if quarter else "BCTC: không có"
    news = f"tin tức thu từ {_d(news_since)}" if news_since else "tin tức: chưa thu"
    horizon = decision.get("Time Horizon")
    summary = decision.get("Executive Summary") or "không nêu"
    lines = [
        f"{ticker} ({facts.exchange}) · phân tích ngày {_d(date.fromisoformat(analysis_date))}",
        f"Dữ liệu: giá DNSE đến {_d(facts.last_bar)} · {statements} · {news}",
        f"Đóng cửa gần nhất {vn_num(facts.close)} (nghìn đồng); biên độ {facts.exchange} ±{round(band * 100)}%"
        + ("" if facts.exchange.upper() in ("HOSE", "HNX") else _ESTIMATED_REFERENCE)
        + f": {vn_num(facts.close * (1 - band))} – {vn_num(facts.close * (1 + band))}",
        f"Xếp hạng: {decision.get('Rating') or 'không nêu'} — chưa được kiểm chứng, chỉ để nghiên cứu",
        "",
        "Mức giá agent điền vào ô riêng (đã kiểm tra biên độ và vùng giá 60 phiên):",
        "  " + " · ".join(f"{label}: {vn_num(kept[key]) if key in kept else 'không nêu'}"
                          for key, label in _LABELS.items()),
        *[f"  {n}" for n in notes],
        "",
        "Ý kiến agent (chưa kiểm chứng; số trong đoạn này KHÔNG được kiểm tra):",
        *[f"  {line}" for line in summary.splitlines()],
        f"  Thời gian nắm giữ: {horizon if horizon and horizon != 'not provided' else 'không nêu'}",
        "Báo cáo đầy đủ: file đính kèm",
    ]
    return "\n".join(lines)
