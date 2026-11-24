"""Vietnam market preset for TradingAgents (HOSE/HNX/UPCoM via DNSE OpenAPI)."""

from __future__ import annotations

import re

from tradingagents.default_config import build_default_config

VN_SUFFIX = ".VN"
VN_BENCHMARK = "VNINDEX"
VN_ANALYSTS = ("market", "fundamentals", "news")
_BASE = re.compile(r"[A-Z0-9]{3,10}")


def normalize_ticker(raw: str) -> str:
    """'vnm' -> 'VNM.VN'; anything that is not a plain 3-10 char code raises ValueError."""
    sym = raw.strip().upper()
    base = sym[: -len(VN_SUFFIX)] if sym.endswith(VN_SUFFIX) else sym
    if not _BASE.fullmatch(base):
        raise ValueError(f"invalid Vietnamese ticker: {raw!r}")
    return base + VN_SUFFIX


def vn_config() -> dict:
    cfg = build_default_config()  # reads TRADINGAGENTS_* now, after .env is loaded, not at import
    cfg["data_vendors"].update(core_stock_apis="dnse", technical_indicators="dnse",
                               fundamental_data="vsi", news_data="vsi", macro_data="vsi", prediction_markets="vsi")
    # first, so resolve_benchmark matches .VN before the "" (SPY) fallback
    cfg["benchmark_map"] = {VN_SUFFIX: VN_BENCHMARK, **cfg["benchmark_map"]}
    cfg.update(output_language="Vietnamese", llm_provider="openai", max_tokens=4096)
    return cfg
