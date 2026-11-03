def test_tradingagents_pinned():
    import tradingagents
    assert tradingagents.__version__ == "0.7.1"


def test_stats_handler_importable():
    from cli.stats_handler import StatsCallbackHandler
    assert StatsCallbackHandler().llm_calls == 0
