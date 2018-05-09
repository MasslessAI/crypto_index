import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt

from cqt.error_msg import error
from cqt.model.valuation_parameters import ValuationParameters
from cqt.model.asset_model_component_spot import AssetModelComponentSpot
from cqt.model.asset_model_component_fwd import AssetModelComponentFwd
from cqt.model.asset_model_component_vol import AssetModelComponentVol


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

    def get_prices_close(self, time):
        price_dict = {}
        for target in self.model_dict.keys():
            component = self.model_dict[target]
            price_dict[component.target] = component.get_price_close(time)

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
        corr = {}
        for i in range(-5, 5):
            corr[i] = log_returns[target_1].corr(log_returns[target_2].shift(i))
        return corr

