#!/usr/bin/python

"""
# Crypto Index API

This is a minimalistic demo of flask-restful api for query data

## To start the demo
$python crypto_index_api.py

## To submit query

### index
curl localhost:5000

### Spot Data
curl localhost:5000/rate/btc

### Hist Data
curl localhost:5000/histdata/btc/20110503/20110523


requires:
* flask
* flask_restful
* numpy
"""

from flask import Flask, jsonify
from flask_restful import Resource, Api
import sqlite3
import numpy as np
from datetime import datetime, timedelta

DB_PATH = './crypto_index.db'
DEBUG_MODE = True

app = Flask(__name__)
api = Api(app)


#Helper
def genDateList(begDate, endDate):
    print((endDate-begDate).days)
    dateList = [begDate+timedelta(i) for i in range((endDate-begDate).days+1)]
    return dateList

def connectDB(dbPath=DB_PATH):
    conn = sqlite3.connect(dbPath)
    return conn

class Index(Resource):
    def get(self):
        return {'Index': 'Hello! Welcome to the crypto index API',
                'From': 'massless.ai',
                'Spot Rate': 'rate/<asset_id>',
                'Hist Data': 'histdata/<asset_id>/<begDate in YYYYMMDD>/<endDate in YYYYMMDD>',
        }


class ExchangeRate(Resource):
    def get(self, asset_id):
        exchangeRate = {}
        exchangeRate['asset_id'] = asset_id
        exchangeRate['timestamp'] = self._getTimeStamp()
        exchangeRate['rate'] = self._getExchangeRate(asset_id)
        return jsonify(exchangeRate)
    
    def _getTimeStamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def _getExchangeRate(self, asset_id):
        return np.abs(np.random.randn(1)[0])

class HistData(Resource):
    def get(self, asset_id, begDateStr, endDateStr):
        begDate = datetime.strptime(begDateStr, '%Y%m%d')
        endDate = datetime.strptime(endDateStr, '%Y%m%d')
        dateList = genDateList(begDate, endDate)
        histdata = {}
        histdata['asset_id'] = asset_id
        histdata['timestamp'] = self._getTimeStamp()
        histdata['x'] = self._getXValue(asset_id, dateList)
        histdata['y'] = self._getYValue(asset_id, dateList)
        return jsonify(histdata)
    
    def _getTimeStamp(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')

    def _getXValue(self, asset_id, dateList):
        return [date.strftime('%Y-%m-%d %H:%M:%S.%f') for date in dateList]

    def _getYValue(self, asset_id,dateList):
        length = len(dateList)
        return np.abs(np.random.randn(length)).tolist()

api.add_resource(Index, '/')
api.add_resource(ExchangeRate, '/rate/<string:asset_id>')
api.add_resource(HistData, '/histdata/<string:asset_id>/<string:begDateStr>/<string:endDateStr>')

if __name__ == '__main__':
    app.run(debug=DEBUG_MODE)