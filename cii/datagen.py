import os
import sys
import requests
import pandas as pd
import csv


def error(msg):
    print(msg)
    sys.exit(64)


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

        for key in request:
            df[key] = request[key]

        if write_to_file:
            data_path = '../data/'
            data_file = source + '_' + get_req_str(source, request, False) + '_data.csv'
            df.to_csv(data_path + data_file, sep=',', encoding='utf-8')

        return df
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