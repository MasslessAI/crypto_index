import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy

from cqt.error_msg import error


class MktEnvSec(object):
    def __init__(self, target, indexed_data, config=None):
        """
        Initialize a market environment section, e.g. BTC.

        :param target: target coin/token/asset unique id
        :param indexed_data: historical and live data with identifier
        :param config: configurations to control the environment set ups
        """
        self.target = target
        self.data = copy.deepcopy(indexed_data.data)
        self.data_info = indexed_data.index
        if config is None:
            self.config = {}
        else:
            self.config = config


class MktEnv(object):
    def __init__(self, section_list):
        """
        create a collection of market environment based on a list of envr sections
        :param section_list:
        """
        model_dict = {}

        if len(section_list) > 0 and 'period_id' in section_list[0].data_info:
            freq = section_list[0].data_info['period_id']

        for i in range(len(section_list)):
            model_dict[section_list[i].target] = section_list[i]
            if 'period_id' in section_list[i].data_info:
                if section_list[0].data_info['period_id'] != freq:
                    error('All the sections in the list should have the data with same freq.')

        self.model_dict = model_dict

    def get_targets(self):
        targets = []
        for asset in self.model_dict.keys():
            targets.append(asset)
        return targets

    def get_prices_close(self, time):
        price_dict = {}
        for target in self.model_dict.keys():
            section = self.model_dict[target]
            price_dict[section.target] = section.get_price_close(time)

        return price_dict

    def get_prices_close_frame(self):
        price_frame = pd.DataFrame()
        for target in self.model_dict.keys():
            section = self.model_dict[target]
            df = section.get_price_close().to_frame().copy()
            df.columns = target + '_' + df.columns
            if len(price_frame) == 0:
                price_frame = df
            else:
                price_frame = pd.merge(price_frame, df, left_index=True, right_index=True)

        return price_frame

    def insert_section(self, section):
        model_dict = self.model_dict
        model_dict[section.target] = section
        self.model_dict = model_dict

    def has_section(self, target):
        if target in self.model_dict.keys():
            return True
        else:
            return False

    def get_section(self, target):
        return self.model_dict[target]

    def get_sections(self, target_list=None):
        if target_list is None:
            target_list = self.get_targets()

        select_model_dict = {}
        for target in target_list:
            select_model_dict[target] = self.get_section(target)

        return select_model_dict

    def get_stats(self, target_list=None):
        if target_list is None:
            target_list = self.get_targets()

        stats = {}
        for target in target_list:
            stats[target] = self.get_section(target).stat()

        return stats

    def sim_prices_close_frame(self, num_regimes=1, time_start=None, time_end=None):
        price_frame = pd.DataFrame()
        for target in self.model_dict.keys():
            section = self.model_dict[target]
            df = section.sim_price_close(num_regimes, time_start, time_end).to_frame().copy()
            df.columns = [target + '_price_close_sim']
            if len(price_frame) == 0:
                price_frame = df
            else:
                price_frame = pd.merge(price_frame, df, left_index=True, right_index=True)

        return price_frame
