""" This module contains functions for generating reports for strategies. """

import os
from typing import Union

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

import matplotlib as mpl
import quantstats as qs


def matplotlib_report(plots: dict[str, pd.Series], title: str,
           purchase_history: Union[dict[str, pd.DataFrame], None] = None) -> None:
    """
    Plots the profit/loss of the specified plots, and the buy and sell points if purchase_history is specified.

    :param dict[str, pd.Series] plots: dictionary mapping the name of the plot to the plot, where the plot is a
    pandas Series of the profit/loss of the plot indexed by the datetime
    :param str title: the title of the report
    :param dict[str, pd.DataFrame] purchase_history: dictionary mapping the name of the plot to the purchase history
    of the plot, where the purchase history is a pandas DataFrame of the buy and sell points indexed by the datetime
    :return: None
    """

    for plot_name, plot in plots.items():
        profits = (plot - plot[0]) / plot[0] * 100
        plt.plot(profits, label=f'{plot_name} - sharpe: {qs.stats.sharpe(plot):.2f}', zorder=1)

        marker_size = mpl.rcParams['lines.markersize']

        # plot buy and sell points
        if purchase_history is not None and plot_name in purchase_history:
            buy_history = purchase_history[plot_name][purchase_history[plot_name]['side'] == 'buy']
            buy_prices = profits[profits.index.searchsorted(buy_history.index) - 1]

            sell_history = purchase_history[plot_name][purchase_history[plot_name]['side'] == 'sell']
            sell_prices = profits[profits.index.searchsorted(sell_history.index) - 1]

            plt.scatter(buy_prices.index, buy_prices - marker_size, marker='^', color='g', zorder=1)
            plt.scatter(sell_prices.index, sell_prices + marker_size, marker='v', color='r', zorder=1)

    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))

    plt.title(title)
    plt.tight_layout()
    plt.legend()

    title = title.replace(" ", "_").lower()

    if not os.path.exists('reports/matplotlib'):
        os.makedirs('reports/matplotlib')

    filepath = f'{os.getcwd()}/reports/matplotlib/{title.replace(" ", "_")}_report.png'
    plt.savefig(filepath)

    print(f'Matplotlib report generated in file://{filepath}')
