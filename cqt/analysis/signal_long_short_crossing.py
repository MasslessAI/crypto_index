import numpy as np
import pandas as pd
import copy
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.model import asset_model
from cqt.model import asset_model_component_spot
from cqt.model.valuation_parameters import ValuationParametersMovingAverage


def signal_long_short_average(model, asset, time=None, val_param=None):
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
    component = model.get_component(asset)

    if time is None:
        time = component.data.index[-1]
    else:
        time = datetime.strptime(time[:10], '%Y-%m-%d')

    if component.data.size < window_long + 2:
        error('Cannot calculate the moving average. The series is too short.')

    factor = ma_param.damping_factor

    series_short = component.get_close_moving_average(window_short, time, factor)
    series_long = component.get_close_moving_average(window_long, time, factor)

    if series_short.iloc[-1] > (1 + ma_param.tolerance_up) * series_long.iloc[-1]:
        return -1
    elif series_short.iloc[-1] < (1 - ma_param.tolerance_down) * series_long.iloc[-1]:
        return 1
    else:
        return 0


def signal_average_envelope(model, asset, time=None, val_param=None):
    if val_param is None:
        val_param = {'window_size': [5],
                     'tolerance_up': 0.025,
                     'tolerance_down': 0.025,
                     'damping_factor': 1.0}

    ma_param = ValuationParametersMovingAverage(val_param)
    if len(ma_param.window_size) != 1:
        error('The window size list needs to be of size 1')
    window_size = ma_param.window_size[0]

    component = model.get_component(asset)

    if time is None:
        time = component.data.index[-1]

    if component.data.size < window_size + 2:
        error('Cannot calculate the moving average. The series is too short.')

    factor = ma_param.damping_factor

    price = component.get_price_close(time)
    ma = component.get_close_moving_average(window_size, time, factor)

    if price > (1 + ma_param.tolerance_up) * ma.iloc[-1]:
        return -1
    elif price < (1 - ma_param.tolerance_down) * ma.iloc[-1]:
        return 1
    else:
        return 0
