import cqt
from cqt.env.mkt_env import MktEnv
from cqt.ledger.ledger import Ledger
from cqt.error_msg import error
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy
import pandas as pd
import sys


class Strategy(object):
    def __init__(self, env, initial, rules):
        """
        Set up a strategy env, feed in the data and initial status of the ledger

        :param env: market env collection
        :param initial: initial ledger status
        :param rules: controls over the strategy
        """
        self.env = env
        self.initial = initial
        self.rules = rules

    def apply_event_logic(self, time, ledger, price_list=None):
        return ledger

    def back_testing(self, start_date=None, end_date=None, lag=3):
        report_col = ['date', 'total', 'pnl', 'cash', 'set_aside']
        for asset in self.env.get_targets():
            report_col.append(asset + '_holding')
            report_col.append(asset + '_price')

        report = pd.DataFrame(columns=report_col)
        asset_prices_frame = self.env.get_prices_close_frame()
        ledger = Ledger(copy.deepcopy(self.initial.holdings), self.initial.cash)

        # debug
        # print(asset_prices_frame)

        if start_date is None:
            start_date = asset_prices_frame.index[lag+1]
        if end_date is None:
            end_date = asset_prices_frame.index[-1]

        asset_prices = self.env.get_prices_close(start_date)
        report_0 = [start_date, ledger.value(asset_prices), 0, ledger.cash, ledger.wife_pocket]
        for asset in self.env.get_targets():
            asset_hold = 0
            if asset in ledger.holdings.keys():
                asset_hold = ledger.holdings[asset]

            report_0.append(asset_hold)
            report_0.append(asset_prices[asset])

        report.loc[0] = report_0

        idx = 1

        for i in range(len(asset_prices_frame.index)-lag-2):
            time = asset_prices_frame.index[i+lag+2]
            # print(start_date, time, end_date) # debug
            if start_date < time < end_date:
                self.apply_event_logic(time, ledger)
                asset_prices = self.env.get_prices_close(time)
                report_i = [time, ledger.value(asset_prices),
                            ledger.value(asset_prices) - report.iloc[idx-1]['total'],
                            ledger.cash, ledger.wife_pocket]
                for asset in self.env.get_targets():
                    asset_hold = 0
                    if asset in ledger.holdings.keys():
                        asset_hold = ledger.holdings[asset]

                    report_i.append(asset_hold)
                    report_i.append(asset_prices[asset])

                report.loc[idx] = report_i
                idx = idx + 1

        plt.plot(report['date'], report['total'])
        for asset in self.env.get_targets():
            plt.plot(report['date'], report[asset + '_price'] * self.initial.cash / report[asset + '_price'][0])
        plt.show()

        plt.plot(report['date'], report['pnl'])
        plt.show()

        return report

    # def sim_testing(self, num_regimes=1, start_date=None, end_date=None, lag=3):
    #     report_col = ['date', 'total', 'pnl', 'cash', 'set_aside']
    #     for asset in self.env.get_targets():
    #         report_col.append(asset + '_holding')
    #         report_col.append(asset + '_price')
    #
    #     report = pd.DataFrame(columns=report_col)
    #     print(num_regimes)
    #     asset_prices_frame = self.env.sim_prices_close_frame(num_regimes, start_date, end_date)
    #     ledger = Ledger(copy.deepcopy(self.initial.holdings), self.initial.cash)
    #
    #     # debug
    #     # print(asset_prices_frame)
    #
    #     if start_date is None:
    #         start_date = asset_prices_frame.index[lag+1]
    #     if end_date is None:
    #         end_date = asset_prices_frame.index[-1]
    #
    #     asset_prices = self.env.get_prices_close(start_date)
    #     report_0 = [start_date, ledger.value(asset_prices), 0, ledger.cash, ledger.wife_pocket]
    #     for asset in self.env.get_targets():
    #         asset_hold = 0
    #         if asset in ledger.holdings.keys():
    #             asset_hold = ledger.holdings[asset]
    #
    #         report_0.append(asset_hold)
    #         report_0.append(asset_prices[asset])
    #
    #     report.loc[0] = report_0
    #
    #     idx = 1
    #
    #     for i in range(len(asset_prices_frame.index)-lag-2):
    #         time = asset_prices_frame.index[i+lag+2]
    #         # print(start_date, time, end_date) # debug
    #         if start_date < time < end_date:
    #             self.apply_event_logic(time, ledger)
    #             asset_prices = self.env.get_prices_close(time)
    #             report_i = [time, ledger.value(asset_prices),
    #                         ledger.value(asset_prices) - report.iloc[idx-1]['total'],
    #                         ledger.cash, ledger.wife_pocket]
    #             for asset in self.env.get_targets():
    #                 asset_hold = 0
    #                 if asset in ledger.holdings.keys():
    #                     asset_hold = ledger.holdings[asset]
    #
    #                 report_i.append(asset_hold)
    #                 report_i.append(asset_prices[asset])
    #
    #             report.loc[idx] = report_i
    #             idx = idx + 1
    #
    #     plt.plot(report['date'], report['total'])
    #     for asset in self.env.get_targets():
    #         plt.plot(report['date'], report[asset + '_price'] * self.initial.cash / report[asset + '_price'][0])
    #     plt.show()
    #
    #     plt.plot(report['date'], report['pnl'])
    #     plt.show()
    #
    #     return report









