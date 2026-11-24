import re
from datetime import date

from vsi.summary import BANDS, MarketFacts, build_summary, check_levels, parse_fields, vn_num

DECISION = """**Rating**: Underweight

**Executive Summary**: Giảm dần tỷ trọng; theo dõi vùng 12,8–13,0 nghìn đồng
và SMA 200 khoảng 15,5766 nghìn đồng.

**Investment Thesis**: Lợi nhuận quý III giảm 57,5%.

**Price Target**: not provided

**Time Horizon**: Các quý tới"""

TRADER = """**Action**: Sell

**Reasoning**: Giá 13,40 dưới SMA 200.

**Entry Price**: not provided

**Stop Loss**: 12.93

**Position Sizing**: Giảm về 50%.

FINAL TRANSACTION PROPOSAL: **SELL**"""

FACTS = MarketFacts(exchange="HNX", last_bar=date(2026, 11, 23), close=13.4, low60=11.9, high60=14.6)


def test_parse_fields():
    d, t = parse_fields(DECISION), parse_fields(TRADER)
    assert d["Rating"] == "Underweight"
    assert d["Executive Summary"].startswith("Giảm dần") and d["Executive Summary"].endswith("15,5766 nghìn đồng.")
    assert d["Price Target"] == "not provided" and d["Time Horizon"] == "Các quý tới"
    assert t["Stop Loss"] == "12.93" and t["Entry Price"] == "not provided"


def test_vn_num():
    assert vn_num(52.3) == "52,30"
    assert vn_num(2126000, 0) == "2.126.000"
    assert vn_num(1001.99) == "1.001,99"


def test_check_levels_boundaries():
    band = BANDS["HOSE"]  # close 52.3 -> next-session band 48.639..55.961
    kept, notes = check_levels({"entry": 55.95, "stop": None, "target": None}, 52.3, 50.0, 56.0, band)
    assert kept == {"entry": 55.95} and notes == []
    kept, notes = check_levels({"entry": 55.97, "stop": 0, "target": None}, 52.3, 50.0, 56.0, band)
    assert kept == {} and len(notes) == 1 and "55,97" in notes[0]
    low_edge = 50.0 * 0.93
    kept, _ = check_levels({"entry": None, "stop": low_edge, "target": None}, 52.3, 50.0, 56.0, band)
    assert kept == {"stop": low_edge}
    kept, notes = check_levels({"entry": None, "stop": low_edge * 0.99, "target": 56.0 * 1.07 + 0.01},
                               52.3, 50.0, 56.0, band)
    assert kept == {} and len(notes) == 2


def test_levels_in_vnd_are_dropped():
    kept, notes = check_levels({"entry": 52000.0, "stop": None, "target": None}, 52.3, 50.0, 56.0, 0.07)
    assert kept == {} and "52.000,00" in notes[0]


def _summary(**kw):
    args = dict(ticker="SHS", analysis_date="2026-11-23", facts=FACTS,
                quarter=(date(2026, 9, 30), date(2026, 10, 21)), news_since=date(2026, 11, 25),
                decision_md=DECISION, trader_md=TRADER)
    return build_summary(**(args | kw))


def test_summary_order_and_labels():
    out = _summary().splitlines()
    text = "\n".join(out)
    order = ["SHS (HNX) · phân tích ngày 23/11/2026", "Đóng cửa gần nhất 13,40",
             "Xếp hạng: Underweight — chưa được kiểm chứng", "Mức giá agent điền vào ô riêng",
             "Ý kiến agent (chưa kiểm chứng; số trong đoạn này KHÔNG được kiểm tra)"]
    positions = [text.index(o) for o in order]
    assert positions == sorted(positions)
    assert "biên độ HNX ±10%: 12,06 – 14,74" in text
    assert "Cắt lỗ: 12,93" in text and "Vào lệnh: không nêu" in text and "Mục tiêu: không nêu" in text
    assert "BCTC quý 30/09/2026 (tạo 21/10/2026)" in text and "tin tức thu từ 25/11/2026" in text
    assert out[-1] == "Báo cáo đầy đủ: file đính kèm"


def test_summary_numbers_outside_opinion_block():
    head = _summary().split("Ý kiến agent")[0]
    llm_numbers = set(re.findall(r"\d+(?:[.,]\d+)*", DECISION.split("**Price Target**")[0]))
    allowed = {"13,40", "12,06", "14,74", "12,93", "23", "11", "2026", "30", "09", "21", "25", "10"}
    leaked = {n for n in llm_numbers - allowed if re.search(rf"(?<![\d,.]){re.escape(n)}(?![\d,.])", head)}
    assert leaked == set()


def test_summary_missing_fields():
    out = _summary(decision_md="**Rating**: Hold", trader_md="", quarter=None, news_since=None)
    assert "BCTC: không có" in out and "tin tức: chưa thu" in out
    assert "Thời gian nắm giữ: không nêu" in out and "Xếp hạng: Hold" in out
