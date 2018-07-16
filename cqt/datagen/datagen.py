import os
import sys
import requests
import pandas as pd
import pickle
import json
from datetime import datetime
from time import mktime
from copy import deepcopy


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

    def copy(self):
        self.data = self.data.copy()

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


def data_gen(source, request, keyList=None, write_to_file=False, sync_to_db=True, returnDF=False):
    
    cfg_file = '%s/api.cfg' % (os.path.dirname(os.path.realpath(__file__)))
    api_cfg = read_api_cfg(cfg_file)
	
    if source in api_cfg.keys():
        source_url = api_cfg[source]['url']
        request_str = get_req_str(source, request)
        request_url = source_url + request_str
        print(request_url)
        if not keyList is None:
            for key in keyList:
                if "header" in api_cfg[source].keys() and not key is None:
                    headers = {api_cfg[source]['header']: key}
                    response = requests.get(request_url, headers=headers)
                else:
                    response = requests.get(request_url)
                if response.status_code == 200:
                    break
                else:
                    print("Response yields a status code of %i (non-200), trying for next key" % response.status_code)
        if response.status_code != 200:
            print(response.text)
            error('response yields %i status code, exiting...'%response.status_code)
            
        
        json_str = response.json()
        #print(json_str)
        df = pd.DataFrame()
        #df = df.append(json_str, ignore_index=True)

        df = covert_data(source,df,json_str)

        # for key in request:
            # df[key] = request[key]
        # if not 'time_end' in df.keys():
            # now_str = "{:%Y-%m-%dT%H:%M:%S}".format(datetime.now())
            # df['time_end'] = df.apply(lambda row: now_str,axis=1)
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
        
        # if sync_to_db:
            # db_path = '../data/database/historical_timeseries.db'
            # engine = create_engine('sqlite:///%s' % db_path)
            # conn = engine.connect()
            
            # df_btc_1d.to_sql('GEMINI_SPOT_BTC_USD', conn, if_exists='replace')
            
            # conn.close()
        
        if returnDF:
            return df
        return indexed_data
    else:
        error('The source or request is not supported.')


def get_req_str(source, request, for_url=True):
    if len(request) == 0:
        error('The input request dictionary cannot be empty.')

    if 'request_type' not in request:
        error('The request dictionary must contain the request type.')

    request_str = ''
    cfg_file = '%s/api.cfg' % (os.path.dirname(os.path.realpath(__file__)))
    api_cfg = read_api_cfg(cfg_file)
	
    
    
    if source in api_cfg.keys():
        request_type = request.get('request_type')
        if request_type not in api_cfg[source]['data'].keys():
            error('The request type is currently not supported.')
		
        request_str = request_str + request_type
        unix_time_flag = api_cfg[source]['unix_time']
        if for_url:
            for attr in api_cfg[source]['data'][request_type]:
                if attr[0] in request:
                    if "time_" in attr[0] and unix_time_flag == 'true':
                        t = datetime.strptime(request.get(attr[0]), "%Y-%m-%dT%H:%M:%S")
                        t_unix = str(int(mktime(t.timetuple())+1e-6*t.microsecond))
                        request_str = request_str + attr[1] + t_unix
                    else:
                        request_str = request_str + attr[1] + request.get(attr[0])
        else:
            request_str = source + '-' + request_str
            if 'symbol_id' in request:
                request_str = request_str + '-' + request.get('symbol_id')
            if 'period_id' in request:
                request_str = request_str + '-' + request.get('period_id')
        return request_str	
    else:
        error('The source is not supported.')
	
    # if source == 'coinapi':
        # if 'request_type' not in request:
            # error('The request dictionary must contain the request type.')

        # request_str = request_str + request.get('request_type')

        # if for_url:
            # if 'symbol_id' in request:
                # request_str = request_str + '/' + request.get('symbol_id')
            # if 'period_id' in request:
                # request_str = request_str + '/history?period_id=' + request.get('period_id')
            # if 'time_start' in request:
                # request_str = request_str + '&time_start=' + request.get('time_start')
            # if 'time_end' in request:
                # request_str = request_str + '&time_end=' + request.get('time_end')
            # if 'include_empty_item' in request:
                # request_str = request_str + '&include_empty_item=' + request.get('include_empty_item')
            # if 'limit' in request:
                # request_str = request_str + '&limit=' + request.get('limit')
        # else:
            # if 'symbol_id' in request:
                # request_str = request_str + '_' + request.get('symbol_id')
            # if 'period_id' in request:
                # request_str = request_str + '_' + request.get('period_id')

        # return request_str

	# else:
        # error('The source is not supported.')

def read_api_cfg(cfg_file):
	with open(cfg_file,'r') as f:
		cfg_str = f.read()
		cfg_data = json.loads(cfg_str)
	return cfg_data

def covert_data(source,data,json_str):
	
	if source == "coinapi":
		data = data.append(json_str, ignore_index=True)
		df_out = convert_coinapi_data(data)
	elif source == "cryptocompare":
		data = data.append(json_str["Data"], ignore_index=True)
		df_out = convert_cryptocompare_data(data)
	elif source == "gdax":
		#data = data.append(json_str, ignore_index=True)
		df_out = convert_gdax_data(json_str)
	return df_out
	
def convert_coinapi_data(data_coinapi):
    conversion_map = {'price_close': 'price_close',
                      'price_open': 'price_open',
                      'price_high': 'price_high',
                      'price_low': 'price_low',
                      'time_close': 'time_close',
                      'time_open': 'time_open',
                      'trades_count': 'trades_count',
                      'volume_traded': 'volume_traded',
                      'key': 'time_open'}

    data_standard = pd.DataFrame()
    for key in conversion_map.keys():
        if key == 'key':
            data_standard[key] = getDate(data_coinapi[conversion_map[key]])
        else:
            data_standard[key] = data_coinapi[conversion_map[key]]

    return data_standard

def convert_gdax_data(data_gdax):
    header = ['time','low','high','open','close','volumn']
    conversion_map = {'price_close': 'close',
                      'price_open': 'open',
                      'price_high': 'high',
                      'price_low': 'low',
                      'time_close': 'time',
                      'time_open': 'time',
                      'trades_count': 'na',
                      'volume_traded': 'volumn',
                      'key': 'time_open'}

    data_standard = pd.DataFrame()
    tmp_df = pd.DataFrame(data_gdax,columns=header)
    for key in conversion_map.keys():
        if conversion_map[key] == 'time':
            tmp_val = date_unix_to_iso(tmp_df[conversion_map[key]])
            if key == 'key':
                data_standard[key] = tmp_val.split('T')[0]
            else:
                data_standard[key] = tmp_val
        elif conversion_map[key] == 'na':
            data_standard[key] = ''
        else:
            data_standard[key] = tmp_df[conversion_map[key]]

    return data_standard    

def convert_cryptocompare_data(data_cc):
    conversion_map = {'price_close': 'close',
                      'price_open': 'open',
                      'price_high': 'high',
                      'price_low': 'low',
                      'time_close': 'time',
                      'time_open': 'time',
                      'trades_count': 'na',
                      'volume_traded': 'volumeto',
                      'key': 'time_open'}

    data_standard = pd.DataFrame()
    for key in conversion_map.keys():
        if conversion_map[key] == 'time':
            tmp_val = date_unix_to_iso(data_cc[conversion_map[key]])
            if key == 'key':
                data_standard[key] = tmp_val.split('T')[0]
            else:
                data_standard[key] = tmp_val
        elif conversion_map[key] == 'na':
            data_standard[key] = ''
        else:
            data_standard[key] = data_cc[conversion_map[key]]

    return data_standard

def date_unix_to_iso (df):
    t = deepcopy(df)
    for i in t.keys():
        t[i]=datetime.fromtimestamp(df[i]).strftime("%Y-%m-%dT%H:%M:%S")
    return t

def getDate (df):
    t = deepcopy(df)
    for i in t.keys():
        t[i]=df[i].split('T')[0]
    return t