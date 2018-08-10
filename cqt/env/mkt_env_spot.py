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
                self.data.index = self.data.index.round('H')
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

    def sim_price_close(self, num_regimes=1, time_start=None, time_end=None):
        time_spot = self.data.index[-1]

        sim_price_close = pd.Series()
        sim_price_close.index.name = 'time_close'
        sim_price_close.rename('price_close_sim')
        sim_price_close[time_spot] = self.get_price_close(time_spot)

        if num_regimes <= 0:
            error('num_regimes needs to be positive integer.')

        if time_start is None:
            time_start = self.data.index[0]

        if time_end is None:
            time_end = self.data.index[-1]

        time_start = self._round_time(time_start)
        time_end = self._round_time(time_end)

        inter_length = (time_end - time_start) / num_regimes

        for i in range(num_regimes):
            hist_start = time_start + i * inter_length
            hist_end = hist_start + inter_length

            hist_start = self._round_time(hist_start)
            hist_end = self._round_time(hist_end)

            statistics = self.stat(hist_start, hist_end)
            avg = statistics['period_log_return']['mean']
            stdev = statistics['period_log_return']['std']
            count = int(statistics['period_log_return']['count'])

            # TODO: use ARIMA for sampling
            # Here we use p(t_i+1) = p(t_i) * exp( (avg+stdev*N(0,1)) * (t_i+1-t_i) )
            norm_vec = np.random.normal(avg, stdev, count-1)

            for j in range(count-1):
                # TODO: only handle hourly or daily data.
                if self.data_info['period_id'] == '1HRS':
                    sim_time = sim_price_close.index[-1] + timedelta(hours=1)
                else:
                    sim_time = sim_price_close.index[-1] + timedelta(days=1)

                sim_time = self._round_time(sim_time)
                sim_price_close[sim_time] = sim_price_close.values[-1] * np.exp(norm_vec[j])

        return sim_price_close

    def plot_sim_close(self, num_regimes=1):
        df = self.sim_price_close(num_regimes)
        plt.plot(df.index, df.values)

        df2 = self.get_price_close()
        plt.plot(df2.index, df2.values)
        plt.show()

    def _round_time(self, time):
        if 'period_id' in self.data_info:
            if self.data_info['period_id'] == '1DAY':
                time_round = time.replace(second=0, microsecond=0, minute=0, hour=0, day=time.day)\
                             + timedelta(days=time.hour//12)
            elif self.data_info['period_id'] == '1HRS':
                time_round = time.replace(second=0, microsecond=0, minute=0, hour=time.hour)\
                             + timedelta(hours=time.minute//30)
            else:
                pass
        else:
            pass

        return time_round
