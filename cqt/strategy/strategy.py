import cqt
from cqt.model.asset_model import AssetModel
from cqt.portfolio import portfolio
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy
import pandas as pd
import sys


def error(msg):
    print(msg)
    sys.exit(64)


class Strategy(object):
    def __init__(self, mdl, ini_prtf, rules):
        self.asset_model = mdl
        self.initial_portfolio = ini_prtf
        self.rules = rules

    def apply_event_logic(self, time, prtf):
        pass

    def back_testing(self, start_date=None, end_date=None, lag=3):
        report_col = ['date', 'total', 'pnl', 'cash', 'set_aside']
        for asset in self.asset_model.get_targets():
            report_col.append(asset + '_holding')
            report_col.append(asset + '_price')

        report = pd.DataFrame(columns=report_col)
        asset_prices_frame = self.asset_model.get_prices_close_frame()
        prtf = portfolio.Portfolio(copy.deepcopy(self.initial_portfolio.asset_holdings),
                                   self.initial_portfolio.cash)
        print(asset_prices_frame)#debug
        if start_date is None:
            start_date = asset_prices_frame.index[lag+1]
        if end_date is None:
            end_date = asset_prices_frame.index[-1]

        asset_prices = self.asset_model.get_prices_close(start_date)
        report_0 = [start_date, prtf.value(asset_prices), 0, prtf.cash, prtf.wife_pocket]
        for asset in self.asset_model.get_targets():
            asset_hold = 0
            if asset in prtf.asset_holdings.keys():
                asset_hold = prtf.asset_holdings[asset]

            report_0.append(asset_hold)
            report_0.append(asset_prices[asset])

        report.loc[0] = report_0

        idx = 1

        for i in range(len(asset_prices_frame.index)-lag-2):
            time = asset_prices_frame.index[i+lag+2]
            print(start_date, time, end_date) # debug
            if start_date < time < end_date:
                self.apply_event_logic(time, prtf)
                asset_prices = self.asset_model.get_prices_close(time)
                report_i = [time, prtf.value(asset_prices),
                            prtf.value(asset_prices) - report.iloc[idx-1]['total'],
                            prtf.cash, prtf.wife_pocket]
                for asset in self.asset_model.get_targets():
                    asset_hold = 0
                    if asset in prtf.asset_holdings.keys():
                        asset_hold = prtf.asset_holdings[asset]

                    report_i.append(asset_hold)
                    report_i.append(asset_prices[asset])

                report.loc[idx] = report_i
                idx = idx + 1

        return report









