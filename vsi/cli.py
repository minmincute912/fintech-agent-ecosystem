"""`vsi analyze TICKER --date YYYY-MM-DD`: one TradingAgents run on a Vietnamese stock."""

from __future__ import annotations

import argparse
import functools
import json
import os
import time
from pathlib import Path

from cli.stats_handler import StatsCallbackHandler
from langchain_core.callbacks import BaseCallbackHandler
from dotenv import load_dotenv
from tradingagents.dataflows.errors import VendorError
from tradingagents.graph.trading_graph import TradingAgentsGraph

from vsi.bridge import install
from vsi.markets import VN_ANALYSTS, normalize_ticker, vn_config
from vsi.dnse import DnseClient
from vsi.news import collect, default_store

DATA_SOURCE = "DNSE OpenAPI"


class ToolCounter(BaseCallbackHandler):
    """Counts tool runs only; a graph-level handler also sees LLM runs, which StatsCallbackHandler already counts."""

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def on_tool_start(self, *args, **kwargs) -> None:
        self.count += 1


def analyze(ticker: str, trade_date: str, *, config: dict | None = None, graph_factory=None) -> dict:
    symbol = normalize_ticker(ticker)
    config = config or vn_config()
    stats = StatsCallbackHandler()
    graph = (graph_factory or TradingAgentsGraph)(selected_analysts=VN_ANALYSTS, config=config, callbacks=[stats])
    tools = ToolCounter()
    # TradingAgents 0.7.1 propagate() calls get_graph_args() without callbacks, so tool runs went uncounted
    graph.propagator.get_graph_args = functools.partial(graph.propagator.get_graph_args, callbacks=[tools])
    started = time.monotonic()
    state, rating = graph.propagate(symbol, trade_date)
    report = graph.save_reports(state, symbol)
    result = {
        "ticker": symbol, "date": trade_date, "rating": rating, "report_path": str(report),
        "llm_calls": stats.llm_calls, "tool_calls": max(stats.tool_calls, tools.count),
        "tokens_in": stats.tokens_in, "tokens_out": stats.tokens_out,
        "seconds": round(time.monotonic() - started, 1),
        "model_quick": config["quick_think_llm"], "model_deep": config["deep_think_llm"],
        "data_source": DATA_SOURCE,
    }
    log = Path(config["results_dir"]) / "vsi_runs.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
    return result


def collect_news() -> int:
    store = default_store()
    result = collect(store)
    for feed, n in result.items():
        print(f"{feed}: {n} new" if isinstance(n, int) else f"{feed}: failed ({n})")
    return 0 if any(isinstance(n, int) for n in result.values()) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="vsi", description="Research only; not investment advice.")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("analyze", help="run the agent team on one Vietnamese ticker")
    p.add_argument("ticker")
    p.add_argument("--date", required=True, help="analysis date, YYYY-MM-DD")
    sub.add_parser("collect-news", help="fetch Vietnamese RSS news into the local store")
    args = parser.parse_args(argv)
    if args.command == "collect-news":
        return collect_news()

    load_dotenv()
    if not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY is not set; add it to .env")
        return 2
    try:
        base = normalize_ticker(args.ticker).removesuffix(".VN")  # reject before any network setup
        client = DnseClient.from_env()
        if client.instrument(base) is None:  # one free DNSE call instead of a full paid LLM run
            print(f"error: {base} is not listed on HOSE, HNX or UPCoM (DNSE)")
            return 2
        install(client)
        result = analyze(args.ticker, args.date)
    except ValueError as e:  # bad ticker/date, missing DNSE keys (VendorNotConfiguredError)
        print(f"error: {e}")
        return 2
    except VendorError as e:  # data source down or rate-limited
        print(f"error: {e}")
        return 1
    print(f"{result['ticker']} {result['date']}: {result['rating']} (research only, not validated)")
    print(f"report: {result['report_path']}")
    print(f"usage: {result['llm_calls']} LLM calls, {result['tokens_in']} in / {result['tokens_out']} out tokens, "
          f"{result['seconds']}s")
    return 0
