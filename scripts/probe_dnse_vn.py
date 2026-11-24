"""Probe DNSE OpenAPI coverage of Vietnamese stocks and VN-Index (M1 Task 8).

Needs DNSE_API_KEY / DNSE_API_SECRET in .env. Prints facts only; never prints keys or signatures.
"""
from datetime import date, timedelta

from dotenv import load_dotenv
from tradingagents.dataflows.errors import VendorError

from vsi.dnse import DnseClient

# HOSE, HNX and UPCoM names, plus ZZZ which should not exist
TICKERS = ["VNM", "FPT", "HPG", "SHS", "PVS", "ACV", "ZZZ"]


def main() -> None:
    load_dotenv()
    client = DnseClient.from_env()
    end = date.today()
    start = end - timedelta(days=5 * 365)
    print(f"run {end}, window {start}..{end}")
    for sym in TICKERS:
        try:
            info = client.instrument(sym)
            df = client.daily_ohlc(sym, start, end)
        except VendorError as e:
            print(f"{sym:5} NO DATA ({e})")
            continue
        move = df["Close"].pct_change().abs()
        worst = f"{move.max():.2%} on {df['Date'][move.idxmax()].date()}" if len(df) > 1 else "n/a"
        print(f"{sym:5} {info} rows={len(df)} first={df['Date'].iloc[0].date()} last={df['Date'].iloc[-1].date()} "
              f"last_close={df['Close'].iloc[-1]} max_abs_daily_move={worst}")
    try:
        idx = client.daily_index("VNINDEX", start, end)
        print(f"VNINDEX rows={len(idx)} first={idx.index[0].date()} last={idx.index[-1].date()} last={idx.iloc[-1]}")
    except VendorError as e:
        print(f"VNINDEX NO DATA ({e})")


if __name__ == "__main__":
    main()
