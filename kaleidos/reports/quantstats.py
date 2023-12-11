""" This module contains functions for generating reports for strategies. """

import os
import warnings
from typing import Union

import pandas as pd
import quantstats as qs

from cubyc.data import Frequency
from cubyc.trading import TradingDSS

warnings.filterwarnings("ignore", category=FutureWarning)


def quantstats_report(dss, value_history: pd.Series, benchmark: Union[str, pd.Series], title: str = None,
                      benchmark_title: str = None, output: str = 'html') -> None:
    """
    Generates a QuantStats report for the specified dss.

    :param DSS dss: the dss to generate the report for
    :param pd.Series value_history: the value history of the dss
    :param Union[str, pd.Series] benchmark: the benchmark to compare the dss to
    :param str title: the title of the report
    :param str benchmark_title: the title of the benchmark
    :param str output: the output of the report, either 'html' or 'plot'
    :return: None
    """
    start_date = value_history.index[0]
    end_date = value_history.index[-1]

    title = dss.name() if title is None else title

    if isinstance(benchmark, str):
        benchmark_title = benchmark if benchmark_title is None else benchmark_title
        market_snapshots = dss.market_datafeed.between(start_date, end_date, 'close', frequency=Frequency.DAY, symbol=benchmark)
    else:
        benchmark_title = 'Benchmark' if benchmark_title is None else benchmark_title
        market_snapshots = benchmark

    value_history.index = pd.DatetimeIndex(value_history.index.date)
    market_snapshots.index = pd.DatetimeIndex(market_snapshots.index.date)

    daily_snapshots = value_history[value_history.index.isin(market_snapshots.index)]

    if output == 'html':
        if not os.path.exists('reports/quantstats'):
            os.makedirs('reports/quantstats')

        file = f'{os.getcwd()}/reports/quantstats/{dss.name}_report.html'

        qs.reports.html(daily_snapshots.pct_change(), output=file, title=title, benchmark=market_snapshots.pct_change(), benchmark_title=benchmark_title)
        print(f'QuantStats report generated in in file://{file}')

    elif output == 'plot':
        qs.reports.full(daily_snapshots.pct_change(), benchmark=market_snapshots.pct_change())
    else:
        raise NotImplementedError
