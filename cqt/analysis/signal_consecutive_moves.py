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


def signal_consecutive_moves(model, asset, time=None, val_param=None):
    if val_param is None:
        val_param = {'method': 'moving_average',
                     'window_size': [10],
                     'tolerance_up': 0.03,
                     'tolerance_down': 0.03}

    if val_param['method'] == 'moving_average':
        ma_param = ValuationParametersMovingAverage(val_param)
        component = model.get_component(asset)
        window_size = ma_param.window_size[0]

        if time is None:
            time = component.data.index[-1]
        else:
            time = datetime.strptime(time[:10], '%Y-%m-%d')

        if component.data.size < window_size + 2:
            error('Cannot calculate the moving average. The series is too short.')

        factor = ma_param.damping_factor

        is_bull = True
        is_bear = True

        average = []
        for i in range(ma_param.calculation_period):
            time_end = time - timedelta(days=i)
            average.append(component.get_close_moving_average(window_size, time_end, factor).iloc[-1])

        for i in range(len(average)-1):
            is_bull = is_bull and (average[i] > (1 - ma_param.tolerance_up) * average[i+1])
            is_bear = is_bear and (average[i] < (1 - ma_param.tolerance_down) * average[i+1])

        if is_bear:
            return -1
        elif is_bull:
            return 1
        else:
            return 0
    else:
        error('Only moving average is implemented for bear market indicator.')
