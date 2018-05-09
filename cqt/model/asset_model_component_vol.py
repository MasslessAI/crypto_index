import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.model.valuation_parameters import ValuationParameters


class AssetModelComponentVol(object):
    def __init__(self, target, data_collection, model_config):
        self.asset_type = 'vol'
        self.target = target
        self.data_collection = data_collection
        self.model_config = model_config

        error('__NOT_IMPLEMENTED__')
