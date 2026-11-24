import pytest
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.memory.settlement import resolve_benchmark

from vsi import bridge
from vsi.markets import VN_BENCHMARK, normalize_ticker, vn_config


def test_normalize_adds_suffix():
    assert normalize_ticker(" vnm ") == "VNM.VN"


def test_normalize_keeps_existing_suffix():
    assert normalize_ticker("VNM.VN") == "VNM.VN"


@pytest.mark.parametrize("bad", ["", "  ", "VN M", "../x", "VNM;ls", "A" * 11, "V"])
def test_normalize_rejects_bad_input(bad):
    with pytest.raises(ValueError):
        normalize_ticker(bad)


def test_vn_config_values():
    cfg = vn_config()
    assert cfg["data_vendors"]["core_stock_apis"] == "dnse"
    assert cfg["data_vendors"]["technical_indicators"] == "dnse"
    assert cfg["output_language"] == "Vietnamese"
    assert cfg["llm_provider"] == "openai"
    assert cfg["max_tokens"] == 4096


def test_vn_config_benchmark():
    assert resolve_benchmark("VNM.VN", vn_config()) == "VNINDEX"


def test_vn_config_leaves_default_untouched():
    vn_config()
    assert DEFAULT_CONFIG["output_language"] == "English"
    assert ".VN" not in DEFAULT_CONFIG["benchmark_map"]


def test_benchmark_is_known_index():
    assert VN_BENCHMARK in bridge.INDEX_CODES
