#!/usr/bin/python3

import os
import sys
import requests
import pandas as pd
import json
from datetime import datetime, date, time

scritDir = os.path.dirname(__file__)
baseUrlCfg = scritDir+'/baseUrl.cfg'
key_CoinAPI = '59103194-7503-441E-A849-1B961471734B'
headers_CoinAPI = {'X-CoinAPI-Key' : key_CoinAPI}
defaultDataDir = '/mnt/d/massless/data'


def reportError(msg):
    print(msg)
    sys.exit(64)

def readTwoColCfg(filePath):
    out = {}
    with open(filePath,'r') as f:
        for line in f.readlines():
            tmp = [elem.replace('\n') for elem in line.split(',')]
            out[tmp[0]] = tmp[1]
    return out

def readJsonCfg(filePath):
    with open(filePath,'r') as f:
        data = json.load(f)
    return data

def getUrlMappingFromJson(filePath):
    data = readJsonCfg(filePath)
    out = {}
    for item in data:
        out[item['key']] = item['url']
    return out

def getUrlTypeMappingFromJson(filePath):
    data = readJsonCfg(filePath)
    out = {}
    for item in data:
        out[item['key']] = item['type']
    return out

def saveData(data,name,format='csv',outDir=defaultDataDir):
    if format == 'csv':
        fileName = '%s/%s' %(outDir, name+'.csv')
        print('---- Saving data to %s' % fileName)
        data.to_csv(fileName)
    elif format == 'pickle':
        fileName = '%s/%s' %(outDir, name+'.pk')
        print('---- Saving data to %s' % fileName)
        data.to_pickle(fileName)
    elif format == 'database':
        print('---- sending to datatbase, somehow...')
    else:
        reportError('Illegal format for saveData function, exiting...')

def getBaseUrl(urlKey):
    urlMap = getUrlMappingFromJson(baseUrlCfg)
    return urlMap[urlKey]

def sendRequest(fullUrl):
    response = requests.get(fullUrl, headers=headers_CoinAPI)
    return response

def parseResponse(response,jsonFormat=False):
    jsonRes = json.loads(response.content.decode('utf-8'))
    if jsonFormat:
        return jsonRes
    else:
        pandasRes = pd.DataFrame(jsonRes)
        return pandasRes

def importFullUrl(fullUrl):

    print('---- Sending request to %s' % fullUrl)
    response = sendRequest(fullUrl)

    print('---- Parsing response')
    pandasRes = parseResponse(response)

    return pandasRes

def importBaseUrl(urlKey):
    baseUrl = getBaseUrl(urlKey)

    print('---- Sending request to %s' % baseUrl)
    response = sendRequest(baseUrl)

    print('---- Parsing response')
    pandasRes = parseResponse(response)

    return pandasRes

def getStaticDataFromAPI(userUrl,userFormat='csv',userOutDir=defaultDataDir):
    urlKey = userUrl
    pandasRes = importBaseUrl(urlKey)
    saveData(pandasRes,urlKey,format=userFormat,outDir=userOutDir)

def buildOHLCVHistoryUrl(symbolID,timeStart,baseUrl='https://rest.coinapi.io/v1/ohlcv',periodID='1DAY',timeEnd='',includeEmptyItems='false',limit='100000'):
    if timeEnd == '':
        timeEnd = datetime.today().isoformat()
        #fullUrl = '%s/%s/history?period_id=%s&time_start=%s&includeEmptyItems=%s&limit=%s' %(baseUrl, symbolID, periodID, timeStart, includeEmptyItems, limit)
    fullUrl = '%s/%s/history?period_id=%s&time_start=%s&time_end=%s&includeEmptyItems=%s&limit=%s' %(baseUrl, symbolID, periodID, timeStart, timeEnd, includeEmptyItems, limit)
    return fullUrl

def getDynamicDataFromAPI(fileName,userUrl,userFormat='csv',userOutDir=defaultDataDir):
    pandasRes = importFullUrl(userUrl)
    saveData(pandasRes,fileName,format=userFormat,outDir=userOutDir)

