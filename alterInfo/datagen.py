import requests
import pandas as pd
import numpy as np

def dataGen(source, request, key, write_to_file):
    if source == 'coinapi':
        sourceurl = 'https://rest.coinapi.io/v1/'
        requesturl = sourceurl + request
        headers = {'X-CoinAPI-Key': key}
        response = requests.get(requesturl, headers=headers)

        jsonStr = response.json()

        df = pd.DataFrame()
        df = df.append(jsonStr, ignore_index=True)

        if write_to_file == True:
            requestStr = request.replace('/','_')
            datapath = '../data/'
            datafile = source + '_' + requestStr + '_data.csv'
            df.to_csv(datapath + datafile, sep=',', encoding='utf-8')

        return df
    else:
        print('The source or request is not supported.')