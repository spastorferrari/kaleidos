""" This module contains functions for generating reports for strategies. """

import os
from typing import Union

import pandas as pd
import quantstats as qs
from cubyc.research import Strategy
from cubyc.data import Frequency

def quantstats_report(strategy: Strategy, value_history: pd.Series, benchmark: Union[str, pd.Series], title: str = None,
                      benchmark_title: str = None, output: str = 'html') -> None:
    """
    Generates a QuantStats report for the specified strategy.

    :param Strategy strategy: the strategy to generate the report for
    :param pd.Series value_history: the value history of the strategy
    :param Union[str, pd.Series] benchmark: the benchmark to compare the strategy to
    :param str title: the title of the report
    :param str benchmark_title: the title of the benchmark
    :param str output: the output of the report, either 'html' or 'plot'
    :return: None
    """
    start_date = value_history.index[0]
    end_date = value_history.index[-1]

    title = strategy.name() if title is None else title

    if isinstance(benchmark, str):
        benchmark_title = benchmark if benchmark_title is None else benchmark_title
        market_snapshots = strategy.market_datafeed.between(start_date, end_date, 'close', frequency=Frequency.DAY, symbol=benchmark)
    else:
        benchmark_title = 'Benchmark' if benchmark_title is None else benchmark_title
        market_snapshots = benchmark

    market_snapshots.index = market_snapshots.index.map(
        lambda t: t.replace(hour=0, minute=0, second=0, microsecond=0, nanosecond=0))

    value_history.index = value_history.index.tz_localize(None)
    market_snapshots.index = market_snapshots.index.tz_localize(None)

    daily_snapshots = value_history[value_history.index.isin(market_snapshots.index)]

    if output == 'html':
        if not os.path.exists('reports/quantstats'):
            os.makedirs('reports/quantstats')

        file = f'{os.getcwd()}/reports/quantstats/{strategy.name()}_report.html'

        qs.reports.html(daily_snapshots.pct_change(), output=file, title=title, benchmark=market_snapshots.pct_change(),
                        benchmark_title=benchmark_title)

        print(f'QuantStats report generated in in file://{file}')
    elif output == 'plot':
        qs.reports.full(daily_snapshots.pct_change(), benchmark=market_snapshots.pct_change())
    else:
        raise NotImplementedError
