"""Probe Yahoo Finance coverage of Vietnamese equities and the VN-Index (M1 Task 2).

Research-only check; prints facts, decides nothing.
"""
import yfinance as yf

EQUITIES = ["VNM.VN", "FPT.VN", "HPG.VN", "SHS.VN", "PVS.VN", "ACV.VN", "SHS.HN"]
INDICES = ["^VNINDEX", "^VNINDEX.VN", "VNINDEX.VN", "^VNI"]


def probe(sym: str) -> str:
    try:
        h = yf.Ticker(sym).history(period="2y", auto_adjust=False, actions=True)
    except Exception as e:  # keep probing the rest
        return f"{sym:14} NO DATA ({type(e).__name__}: {e})"
    if h.empty:
        return f"{sym:14} NO DATA (empty)"
    splits = int((h.get("Stock Splits", 0) != 0).sum())
    divs = int((h.get("Dividends", 0) != 0).sum())
    return (f"{sym:14} rows={len(h):4} first={h.index[0].date()} last={h.index[-1].date()} "
            f"last_close={h['Close'].iloc[-1]:.2f} splits={splits} dividends={divs}")


if __name__ == "__main__":
    for s in EQUITIES + INDICES:
        print(probe(s), flush=True)
