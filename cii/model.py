import os
import sys
import numpy as np
import pandas as pd
from cii import datagen


def error(msg):
    print(msg)
    sys.exit(64)


class SimModel(object):
    def __init__(self, data_collection, model_config):
        self.data_collection = data_collection
        self.model_config = model_config

    def is_bear(self):
        method = self.model_config['indicator_type']
        window_size = self.model_config['window_size']
        tolerance = self.model_config['tolerance']

        series = pd.Series(self.data_collection['price_close'].values, index=self.data_collection['time_close'])

        if method == 'moving_average':
            series = series.rolling(window_size).mean()
            series = series.dropna()

            if len(series) < 3:
                error('The input data is not enough for bear indicator.')

            if series.iloc[-1] < (1 - tolerance) * series.iloc[-2] and \
                    series.iloc[-2] < (1 - tolerance) * series.iloc[-3]:
                return True
            else:
                return False
        else:
            error('Only moving average is implemented for bear market indicator.')
