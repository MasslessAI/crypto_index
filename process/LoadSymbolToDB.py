#!/drives/d/Anaconda/python
import sys
sys.path.append('../')
sys.path.append('/home/cqtrun/dailyRun/env0/bin/crypto_index')
import cqt
import cqt.datagen as dg
import pandas as pd
import numpy as np
import csv
import cqt.dbutility.dbutility as db
# import cli.app
# @cli.app.CommandLineApp


def validate(input_req_dict):
    req_dict = input_req_dict.copy()
    if req_dict['source'] == '':
        reportErr('source of request cannot be empty, exiting...')
    elif req_dict['request_type'] == '':
        reportErr('request_type of request cannot be empty, exiting...')
    elif req_dict['symbol_id'] == '':
        reportErr('symbol_id of request cannot be empty, exiting...')
    elif req_dict['period_id'] == '':
        reportErr('period_id of request cannot be empty, exiting...')
    elif req_dict['time_start'] == '':
        print('time_start is empty, defaulting to 2001-01-01T00:00:00')
        req_dict['time_start'] = '2001-01-01T00:00:00'
    elif req_dict['time_end'] == '':
        print('time_end is empty, deleting this attribute from dictionary')
        req_dict.pop('time_end', None)
    elif req_dict['limit'] == '':
        print('limit is empty, defaulting to 100000')
        req_dict['limit'] = '100000'

    return req_dict


def getApiKey(keyFile):
    with open(keyFile) as f:
        keyList = [row.replace('\n', '') for row in f.readlines()]
    #key = keyList[0]
    return keyList


def loadSingleSymbolToDB(req_dict, keyList):

    my_req_dict = validate(req_dict)
    source = my_req_dict['source']

    my_req_dict.pop('source')

    print('Running Symbol %s, Period %s, on source %s' %
          (my_req_dict['symbol_id'], my_req_dict['period_id'], source))

    df = dg.data_gen(source, my_req_dict, keyList,
                     write_to_file=False, returnDF=True)

    tbl_name = dg.get_req_str(source, my_req_dict, False)

    print('Dumping into table %s' % tbl_name)

    db.dump_to_db(df, tbl_name, 'key')

# def main(app):

    # key = getApiKey(app.params.key_cfg_file)

    # #key = "59103194-7503-441E-A849-1B961471734B"

    # with open(app.params.requestListFile) as f:
    # requestList = [{k: v for k, v in row.items()} for row in csv.DictReader(f)]

    # for req in requestList:
    # loadSingleSymbolToDB(req)


# main.add_param("requestListFile", help='Mandatory, a csv file containing requests on each line')
# main.add_param("key_cfg_file", help='Mandatory, a file with api key on each line')

# main.add_param("symbol", help='Mandatory, symbol id for the request')
# main.add_param("period", help='Mandatory, period for the request')
# main.add_param("-source", default='coinapi' help='Optional, source of the request, default to coinapi')
# main.add_param("-type", default="ohlcv", help='Optional, the type of the request, default to ohlcv')
# main.add_param("-timestart", default='2001-01-01T00:00:00', help='Optional, the start time of the request, default to 2001-01-01T00:00:00')
# main.add_param("-timeend", default=None, help='Optional, the end time of the request, default to None')
# main.add_param("-limit", default='100000', help='Optional, the limit of the request, default to 100000')

# if __name__ == "__main__":

key_cfg_file = sys.argv[1]
requestListFile = sys.argv[2]

keyList = getApiKey(key_cfg_file)
# print(key)

#key = "59103194-7503-441E-A849-1B961471734B"

with open(requestListFile) as f:
    requestList = [{k: v for k, v in row.items()} for row in csv.DictReader(f)]

for req in requestList:
    loadSingleSymbolToDB(req, keyList)
