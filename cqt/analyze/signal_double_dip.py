import numpy as np
import pandas as pd
import copy
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.analyze.val_param import ValParamMovingAverage


def signal_double_dip(env, asset, time=None, val_param=None):
    if val_param is None:
        val_param = {'window_size': [3, 20]}

    if len(val_param['window_size']) != 2:
        error('For double dip, two window sizes need to be provided in the rule.')

    dip_param = ValParamMovingAverage(val_param)
    window_ma = dip_param.window_size[0]
    window_dip = dip_param.window_size[1]
    section = env.get_section(asset)

    series = section.get_price_close()

    if time is None:
        time = series.index[-1]

    if series.index[0] + timedelta(days=window_ma + window_dip) > time:
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

    ind_roots = -27 * a ** 2 * d ** 2 + 18 * a * b * c * d - 4 * a * c ** 3 - 4 * b ** 3 * d + b ** 2 * c ** 2

    if z.item(0) > 0:
        if ind_roots > 0:
            return 1
    else:
        if ind_roots > 0:
            return -1

    return 0

