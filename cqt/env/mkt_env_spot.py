import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.env.mkt_env import MktEnvSec


class MktEnvSpot(MktEnvSec):
    def __init__(self, target, data_collection, config=None):
        super(MktEnvSpot, self).__init__(target, data_collection, config)

        self.type = 'spot'

        time_close = []
        for time in self.data.time_close:
            time_close.append(datetime.strptime(time[:26], '%Y-%m-%dT%H:%M:%S.%f'))
            # time_close.append(datetime.strptime(time[:10], '%Y-%m-%d'))

        self.data.index = pd.to_datetime(time_close)
        self.data.index.name = 'time_close'

        if 'period_id' in self.data_info:
            if self.data_info['period_id'] == '1DAY':
                self.data.index = self.data.index.round('D')
            elif self.data_info['period_id'] == '1HRS':
                self.data.index = self.data.index.dt.round('H')
            else:
                pass

        info_list = ['price_close', 'price_open', 'price_high', 'price_low', 'trades_count',
                     'volume_traded', 'time_open']
        self.data = self.data[info_list]
        self.data['price_mid'] = 0.5 * (self.data['price_high'] + self.data['price_low'])
        self.data['range_open'] = self.data['price_open'] / self.data['price_mid'] - 1
        self.data['range_close'] = self.data['price_close'] / self.data['price_mid'] - 1
        self.data['range_high'] = self.data['price_high'] / self.data['price_mid'] - 1
        self.data['range_low'] = self.data['price_low'] / self.data['price_mid'] - 1
        self.data['period_abs_return'] = self.data['price_mid'].shift(1) / self.data['price_mid'] - 1
        self.data['period_log_return'] = np.log(self.data['price_mid'].shift(1) / self.data['price_mid'])
        self.data.fillna(0)
        # self.data.columns = self.target + '_' + self.data.columns

    def get_price_close(self, time=None):
        if 'price_close' in self.data.columns:
            price_close = 'price_close'
        elif self.target + '_price_close' in self.data.columns:
            price_close = self.target + '_price_close'
        else:
            error('Price close is not in the env section data.')

        if time is None:
            return self.data[price_close]

        series = self.data[price_close]
        series_trunc = series.truncate(after=time)
        return series_trunc.iloc[-1]

    def plot_price_close(self):
        df = self.get_price_close()
        plt.plot(df.index, df.values)
        plt.show()

    def get_log_return(self, time=None):
        if time is None:
            return self.data['period_log_return']

        series = self.data['period_log_return']
        series_trunc = series.truncate(after=time)
        return series_trunc.iloc[-1]

    def plot_log_return(self):
        plt.plot(self.data.index, self.data['period_log_return'])
        plt.show()

    def get_close_moving_average(self, window_size, time=None, damping_factor=None):
        if time is None:
            time_end = self.data.index[-1]
            time_start = self.data.index[0]
        else:
            time_end = time
            time_start = time - timedelta(days=window_size)

        df = self.get_price_close()
        if damping_factor is None:
            ma_series = df.truncate(before=time_start, after=time_end)
            ma_series = ma_series.rolling(window_size).mean()
            ma_series = ma_series.dropna()
        else:
            series = df.truncate(before=time_start, after=time_end)
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
                ma_series.at[window_size + i - 1] = avg

        return ma_series

    def plot_close_moving_average(self, window_sizes, damping_factor=None):
        if len(window_sizes) == 0:
            error('List of window sizes needs to be provided.')

        for size in window_sizes:
            series = self.get_close_moving_average(size, None, damping_factor)
            plt.plot(series.index, series.values)

        plt.show()

    def stat(self, time_start=None, time_end=None):
        """
        calculate the simple statistics on the columns of the section of the environment
        :param time_start:
        :param time_end:
        :return: statistics table
        """
        if time_start is None and time_end is None:
            stat_data = self.data
        elif time_start is None:
            stat_data = self.data.truncate(after=time_end)
        elif time_end is None:
            stat_data = self.data.truncate(before=time_start)
        else:
            stat_data = self.data.truncate(before=time_start, after=time_end)

        result = {}

        for col in stat_data:
            result[col] = stat_data[col].describe()

        return result



