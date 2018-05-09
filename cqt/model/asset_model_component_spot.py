import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.model.valuation_parameters import ValuationParametersMovingAverage


class AssetModelComponentSpot(object):
    def __init__(self, target, data_collection, model_config):
        self.asset_type = 'spot'
        self.target = target
        self.data_collection = data_collection
        self.model_config = model_config

        time_close = []
        for time in self.data_collection.data['time_close']:
            # time_close.append(datetime.strptime(time[:26], '%Y-%m-%dT%H:%M:%S.%f'))
            time_close.append(datetime.strptime(time[:10], '%Y-%m-%d'))

        self.price_open_series = pd.Series(self.data_collection.data['price_open'].values, index=time_close)
        self.price_close_series = pd.Series(self.data_collection.data['price_close'].values, index=time_close)
        self.price_high_series = pd.Series(self.data_collection.data['price_high'].values, index=time_close)
        self.price_low_series = pd.Series(self.data_collection.data['price_low'].values, index=time_close)
        self.trades_count_series = pd.Series(self.data_collection.data['trades_count'].values, index=time_close)

    def get_price_close(self, time=None):
        if time is None:
            return self.price_close_series

        series = self.price_close_series
        series_trunc = series.truncate(after=time)
        return series_trunc.iloc[-1]

    def plot_price_close(self):
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

    def plot_log_returns(self, period):
        ret_series = self.get_log_returns(period)
        plt.plot(ret_series.index, ret_series.values)
        plt.show()

    def get_close_moving_average(self, window_size, damping_factor=None):
        if damping_factor is None:
            ma_series = self.price_close_series.rolling(window_size).mean()
            ma_series = ma_series.dropna()
        else:
            series = self.price_close_series
            series_size = len(series)
            if series_size < window_size:
                error('The input series is shorter than the window size.')

            ma_series = pd.Series()
            for i in range(series_size - window_size):
                avg = 0.0
                for j in range(window_size):
                    scalar = damping_factor ** j
                    avg = avg + scalar * series.iloc[window_size + i - j - 1]
                avg = avg / window_size
                ma_series.set_value(series.index[window_size + i - 1], avg)

        return ma_series

    def plot_close_moving_average(self, window_sizes):
        if len(window_sizes) == 0:
            error('List of window sizes needs to be provided.')

        for size in window_sizes:
            series = self.get_close_moving_average(size)
            plt.plot(series.index, series.values)

        plt.show()

    def signal_bear_or_bull(self, time=None, val_param=None):
        if val_param is None:
            val_param = {'method': 'moving_average',
                         'window_size': [10],
                         'tolerance_up': 0.03,
                         'tolerance_down': 0.03}

        if val_param['method'] == 'moving_average':
            ma_param = ValuationParametersMovingAverage(val_param)
            series = self.price_close_series

            if time is None:
                time = series.index[-1]

            series_trunc = series.truncate(after=time)
            series_trunc = series_trunc.rolling(ma_param.window_size[0]).mean()
            series_trunc = series_trunc.dropna()

            if len(series_trunc) < ma_param.calculation_period + 2:
                error('The input data is not enough for bear indicator.')

            is_bull = True
            is_bear = True

            for i in range(ma_param.calculation_period):
                is_bull = is_bull and (series_trunc.iloc[-1-i] > (1-ma_param.tolerance_up) * series_trunc.iloc[-2-i])
                is_bear = is_bear and (series_trunc.iloc[-1-i] < (1-ma_param.tolerance_down) * series_trunc.iloc[-2-i])

            if is_bear:
                return -1
            elif is_bull:
                return 1
            else:
                return 0
        else:
            error('Only moving average is implemented for bear market indicator.')

    def signal_double_dip(self, time=None, val_param=None):
        if val_param is None:
            val_param = {'window_size': [3, 20]}

        if len(val_param['window_size']) != 2:
            error('For double dip, two window sizes need to be provided in the rule.')

        dip_param = ValuationParametersMovingAverage(val_param)
        window_ma = dip_param.window_size[0]
        window_dip = dip_param.window_size[1]

        series = self.price_close_series

        if time is None:
            time = datetime.strptime(series.index[-1], '%Y-%m-%dT%H:%M:%S.%f')

        if series.index[0] + timedelta(days=window_ma+window_dip) > time:
            error('The given time is early than the series start date plus window.')

        series_trunc = series.rolling(window=window_ma, center=False).mean().dropna()
        end_date = time
        start_date = time - timedelta(days=window_dip)

        series_trunc = series_trunc.truncate(before=start_date, after=end_date)
        y = np.array(list(series_trunc.values))
        x = np.arange(len(y))
        # t = np.array(list(series_trunc.index))
        z = np.polyfit(x, y, 4)

        a = 4 * z.item(0)
        b = 3 * z.item(1)
        c = 2 * z.item(2)
        d = z.item(3)

        ind_roots = -27 * a**2 * d**2 + 18 * a * b * c * d - 4 * a * c**3 - 4 * b**3 * d + b**2 * c**2

        if z.item(0) > 0:
            if ind_roots > 0:
                return 1
        else:
            if ind_roots > 0:
                return -1

        return 0

    def signal_long_short_average(self, time=None, val_param=None):
        if val_param is None:
            val_param = {'window_size': [5, 30],
                         'tolerance_up': 0.0,
                         'tolerance_down': 0.0}

        if val_param['window_size'][0] > val_param['window_size'][1]:
            window_short = val_param['window_size'][1]
            window_long = val_param['window_size'][0]
        else:
            window_short = val_param['window_size'][0]
            window_long = val_param['window_size'][1]

        ma_param = ValuationParametersMovingAverage(val_param)
        series = self.price_close_series

        if time is None:
            time = series.index[-1]

        if series.size < window_long + 2:
            error('Cannot calculate the moving average. The series is too short.')

        factor = ma_param.damping_factor

        series_short = self.get_close_moving_average(window_short, factor)
        series_long = self.get_close_moving_average(window_long, factor)
        series_trunc_short = series_short.truncate(after=time)
        series_trunc_long = series_long.truncate(after=time)

        if series_trunc_short.iloc[-1] > (1 + ma_param.tolerance_up) * series_trunc_long.iloc[-1]:
            return -1
        elif series_trunc_short.iloc[-1] < (1 - ma_param.tolerance_down) * series_trunc_long.iloc[-1]:
            return 1
        else:
            return 0

    def signal_average_envelope(self, time=None, val_param=None):
        if val_param is None:
            val_param = {'window_size': [5],
                         'tolerance_up': 0.025,
                         'tolerance_down': 0.025}

        ma_param = ValuationParametersMovingAverage(val_param)
        if len(ma_param.window_size) != 1:
            error('The window size list needs to be of size 1')
        window_size = ma_param.window_size[0]

        series = self.price_close_series

        if time is None:
            time = series.index[-1]

        if series.size < window_size + 2:
            error('Cannot calculate the moving average. The series is too short.')

        factor = ma_param.damping_factor

        series_trunc = series.truncate(after=time)
        series_ma = self.get_close_moving_average(window_size, factor)
        series_trunc_ma = series_ma.truncate(after=time)

        if series_trunc.iloc[-1] > (1 + ma_param.tolerance_up) * series_trunc_ma.iloc[-1]:
            return -1
        elif series_trunc.iloc[-1] < (1 - ma_param.tolerance_down) * series_trunc_ma.iloc[-1]:
            return 1
        else:
            return 0




