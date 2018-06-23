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

        if len(component_list) > 0 and 'period_id' in component_list[0].data_info:
            freq = component_list[0].data_info['period_id']

        for i in range(len(component_list)):
            model_dict[component_list[i].target] = component_list[i]
            if 'period_id' in component_list[i].data_info:
                if component_list[0].data_info['period_id'] != freq:
                    error('All the components in the list should have the data with same freq.')

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

    def get_prices_close_frame(self):
        price_dict = pd.DataFrame()
        price_dict['lkey']=None
        for target in self.model_dict.keys():
            component = self.model_dict[target]
            print(target)
            # price_dict[component.target]A.merge(B, left_on='lkey', right_on='rkey', how='outer')component.get_price_close()
            df = component.get_price_close().to_frame().reset_index()
            df.columns =['rkey', target]
            if price_dict.empty:
                price_dict = df.copy()
                price_dict.rename(columns={'rkey':'lkey'}, inplace=True)
            else:
                price_dict.merge(df, left_on='lkey', right_on='rkey', how='outer')
            
        price_dict.set_index('lkey', inplace=True)
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


