import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt


def error(msg):
    print(msg)
    sys.exit(64)


class BearBullMarketRules(object):
    def __init__(self, rule_dict):
        if 'method' in rule_dict.keys():
            self.method = rule_dict['method']
        else:
            error('method needs to be given in the rule dict.')

        if rule_dict['method'] == 'moving_average':
            if 'window_size' in rule_dict.keys():
                self.window_size = rule_dict['window_size']
            else:
                error('window_size needs to be given when method = moving_average')
            if 'tolerance_up' in rule_dict.keys():
                self.tolerance_up = rule_dict['tolerance_up']
            else:
                error('tolerance_up needs to be given when method = moving_average')
            if 'tolerance_down' in rule_dict.keys():
                self.tolerance_down = rule_dict['tolerance_down']
            else:
                error('tolerance_down needs to be given when method = moving_average')
        elif rule_dict['method'] == 'multiple_hits':
            error('__NOT_IMPLEMENTED__')
        else:
            error('__NOT_IMPLEMENTED__')


class AssetModelComponent(object):
    def __init__(self, target, data_collection, model_config):
        self.target = target
        self.data_collection = data_collection
        self.model_config = model_config

        time_close = []
        for time in self.data_collection['time_close']:
            time_close.append(datetime.strptime(time[:26], '%Y-%m-%dT%H:%M:%S.%f'))

        self.price_close_series = pd.Series(self.data_collection['price_close'].values,
                                            index=time_close)
        self.trades_count_series = pd.Series(self.data_collection['trades_count'].values,
                                             index=time_close)
        if 'asset_type' not in model_config.keys():
            self.asset_type = 'spot'
        else:
            self.asset_type = model_config['asset_type']

    def get_price(self, time):
        series = self.price_close_series
        series_trunc = series.truncate(after=time)
        return series_trunc.iloc[-1]

    def plot_price(self):
        plt.plot(self.price_close_series.index, self.price_close_series.values)
        plt.show()

    def get_log_returns(self, period):
        if period is None:
            period = '1d'

        log_returns = np.log(self.price_close_series.values) - np.log(self.price_close_series.shift(-1).values)
        time_diffs = []
        for i in range(len(self.price_close_series.index)-1):
            time_diffs.append(self.price_close_series.index[i+1] - self.price_close_series.index[i])

        time_period = timedelta()
        if period == '1d':
            time_period = timedelta(days=1)
        elif period == '1m':
            time_period = timedelta(days=30)
        elif period == '1y':
            time_period = timedelta(days=365)
        else:
            error('Unrecognized period input.')

        for i in range(len(time_diffs)):
            time_diffs[i] = time_diffs[i] / time_period

        log_returns = log_returns[:-1]
        log_returns = np.divide(log_returns, time_diffs)

        return pd.Series(log_returns, index=self.price_close_series.index[:-1])

    def bear_or_bull(self, time=None, rule_dict=None):
        if rule_dict is None:
            rule_dict = {'method': 'moving_average',
                         'window_size': 10,
                         'tolerance_up': 0.03,
                         'tolerance_down': 0.03}

        bear_bull_rules = BearBullMarketRules(rule_dict)

        series = self.price_close_series

        if time is None:
            time = series.index[-1]

        series_trunc = series.truncate(after=time)

        if bear_bull_rules.method == 'moving_average':
            series_trunc = series_trunc.rolling(bear_bull_rules.window_size).mean()
            series_trunc = series_trunc.dropna()

            if len(series_trunc) < 4:
                error('The input data is not enough for bear indicator.')

            if series_trunc.iloc[-1] < (1 - bear_bull_rules.tolerance_up) * series_trunc.iloc[-2] and \
                    series_trunc.iloc[-2] < (1 - bear_bull_rules.tolerance_up) * series_trunc.iloc[-3]:
                return -1
            elif series_trunc.iloc[-1] > (1 + bear_bull_rules.tolerance_down) * series_trunc.iloc[-2] and \
                    series_trunc.iloc[-2] > (1 + bear_bull_rules.tolerance_down) * series_trunc.iloc[-3]:
                return 1
            else:
                return 0
        else:
            error('Only moving average is implemented for bear market indicator.')


class AssetModel(object):
    def __init__(self, component_list):
        model_dict = {}

        for i in range(len(component_list)):
            model_dict[component_list[i].target] = component_list[i]

        self.model_dict = model_dict

    def get_targets(self):
        targets = []
        for asset in self.model_dict.keys():
            targets.append(asset)
        return targets

    def get_prices(self, time):
        price_dict = {}
        for target in self.model_dict.keys():
            component = self.model_dict[target]
            price_dict[component.target] = component.get_price(time)

        return price_dict

    def insert_component(self, component):
        model_dict = self.model_dict
        model_dict[component.target] = component
        self.model_dict = model_dict

    def has_component(self, target):
        if target in self.model_dict.keys():
            return True
        else:
            return False

    def get_component(self, target):
        return self.model_dict[target]

    def get_components(self, target_list):
        select_model_dict = {}
        for target in target_list:
            select_model_dict[target] = self.get_component(target)
        return select_model_dict

    def concat_prices(self, target_1=None, target_2=None):
        if target_1 is not None:
            component_1 = self.get_component(target_1)
            price_1 = component_1.price_close_series

        if target_2 is not None:
            component_2 = self.get_component(target_2)
            price_2 = component_2.price_close_series

        if target_1 is not None and target_2 is not None:
            prices = pd.concat([price_1, price_2], axis=1, join='inner')
            prices.columns = [target_1, target_2]
            return prices
        elif target_1 is not None and target_2 is None:
            return price_1
        elif target_1 is None and target_2 is not None:
            return price_2
        else:
            target_0 = list(self.model_dict.keys())[0]
            component_0 = self.get_component(target_0)
            price_0 = component_0.price_close_series

            for target_i in self.model_dict.keys():
                if target_i != target_0:
                    component_i = self.get_component(target_i)
                    price_i = component_i.price_close_series
                    prices = pd.concat([price_0, price_i], axis=1, join='inner')

            prices.columns = self.model_dict.keys()

            return prices

    def concat_log_return(self, target_1, target_2, period):
        component_1 = self.get_component(target_1)
        return_1 = component_1.get_log_returns(period)

        component_2 = self.get_component(target_2)
        return_2 = component_2.get_log_returns(period)

        returns = pd.concat([return_1, return_2], axis=1, join='inner')
        returns.columns = [target_1, target_2]
        return returns

    def corr_log_return(self, target_1, target_2, period):
        log_returns = self.concat_log_return(target_1, target_2, period)
        corr = log_returns[target_1].corr(log_returns[target_2])
        return corr

