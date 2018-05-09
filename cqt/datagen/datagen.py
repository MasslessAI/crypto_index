import os
import sys
import requests
import pandas as pd
import pickle


def error(msg):
    print(msg)
    sys.exit(64)


class IndexedData(object):
    def __init__(self, source, request_dict, data):
        self.source = source
        self.file_name = source + '_' + get_req_str(source, request_dict, False) + '_data'
        self.index = request_dict
        self.data = data
        self.validate()

    def validate(self):
        if 'price_close' not in self.data.keys():
            error('price_close is not in the input data.')
        if 'price_open' not in self.data.keys():
            error('price_open is not in the input data.')
        if 'price_low' not in self.data.keys():
            error('price_low is not in the input data.')
        if 'price_high' not in self.data.keys():
            error('price_high is not in the input data.')
        if 'time_close' not in self.data.keys():
            error('time_close is not in the input data.')
        if 'time_open' not in self.data.keys():
            error('time_open is not in the input data.')
        if 'trades_count' not in self.data.keys():
            error('trades_count is not in the input data.')
        if 'volume_traded' not in self.data.keys():
            error('volume_traded is not in the input data.')


def data_gen(source, request, key, write_to_file=False):
    if source == 'coinapi':
        source_url = 'https://rest.coinapi.io/v1/'
        request_str = get_req_str(source, request)
        request_url = source_url + request_str
        headers = {'X-CoinAPI-Key': key}
        response = requests.get(request_url, headers=headers)

        json_str = response.json()

        df = pd.DataFrame()
        df = df.append(json_str, ignore_index=True)

        df = convert_coinapi_data(df)

        for key in request:
            df[key] = request[key]

        indexed_data = IndexedData(source, request, df)
        if write_to_file:
            data_path = '../data/csv/'
            data_file_csv = source + '_' + get_req_str(source, request, False) + '_data.csv'
            df.to_csv(data_path + data_file_csv, sep=',', encoding='utf-8')

            data_path = '../data/pickle/'
            data_file_pickle = source + '_' + get_req_str(source, request, False) + '_data.pickle'
            pickle_out = open(data_path + data_file_pickle, "wb")
            pickle.dump(indexed_data, pickle_out)
            pickle_out.close()

        return indexed_data
    else:
        error('The source or request is not supported.')


def get_req_str(source, request, for_url=True):
    if len(request) == 0:
        error('The input request dictionary cannot be empty.')

    request_str = ''

    if source == 'coinapi':
        if 'request_type' not in request:
            error('The request dictionary must contain the request type.')

        request_str = request_str + request.get('request_type')

        if for_url:
            if 'symbol_id' in request:
                request_str = request_str + '/' + request.get('symbol_id')
            if 'period_id' in request:
                request_str = request_str + '/history?period_id=' + request.get('period_id')
            if 'time_start' in request:
                request_str = request_str + '&time_start=' + request.get('time_start')
            if 'time_end' in request:
                request_str = request_str + '&time_end=' + request.get('time_end')
            if 'include_empty_item' in request:
                request_str = request_str + '&include_empty_item=' + request.get('include_empty_item')
            if 'limit' in request:
                request_str = request_str + '&limit=' + request.get('limit')
        else:
            if 'symbol_id' in request:
                request_str = request_str + '_' + request.get('symbol_id')
            if 'period_id' in request:
                request_str = request_str + '_' + request.get('period_id')

        return request_str
    else:
        error('The source is not supported.')


def convert_coinapi_data(data_coinapi):
    conversion_map = {'price_close': 'price_close',
                      'price_open': 'price_open',
                      'price_high': 'price_high',
                      'price_low': 'price_low',
                      'time_close': 'time_close',
                      'time_open': 'time_open',
                      'trades_count': 'trades_count',
                      'volume_traded': 'volume_traded'}

    data_standard = pd.DataFrame()
    for key in conversion_map.keys():
        data_standard[key] = data_coinapi[conversion_map[key]]

    return data_standard
