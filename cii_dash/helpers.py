import os
import sys
from datetime import datetime, timedelta
import sqlite3

from strategies import *

def getdb(dbPath):
    conn = sqlite3.connect(dbPath)
    return conn

def test_strategy( 
                   df_btc,
                   df_eth,
                   init_cash=1000000, 
                   init_btc=0, 
                   init_eth=0, 
                   bb_rule_method='moving_average', 
                   bb_rule_window_size=3,
                   bb_rule_tolerance_up=0.01,
                   bb_rule_tolerance_down=0.01,
                   back_test_start_date=datetime(2018,2,1),
                   strategy_name='strategyTest1'):
    assets={'btc':init_btc, 'eth':init_eth}
    ini_pfo = pfo.Portfolio(assets, init_cash)
    bb_rule={
            'method': bb_rule_method,
            'window_size': [bb_rule_window_size],
            'tolerance_up': bb_rule_tolerance_up,
            'tolerance_down':bb_rule_tolerance_down,
    }


    model_config = {'asset_type': 'spot'}
    model_btc = md.AssetModelComponent('btc', df_btc, model_config)
    model_eth = md.AssetModelComponent('eth', df_eth, model_config)
    asset_model = md.AssetModel([])
    asset_model.insert_component(model_btc)
    asset_model.insert_component(model_eth)


    strats = strategyMetaDict[strategy_name](asset_model, ini_pfo, bb_rule)
    report = strats.back_testing(back_test_start_date)
    report['btc_return'] = report['btc_price'] * init_cash / report['btc_price'][0]
    report['eth_return'] = report['eth_price'] * init_cash / report['eth_price'][0]
    return report
    
def make_candlestick(df, ticker):
    candlestick = {
            'x': df['time_close'],
            'open': df['price_open'],
            'high': df['price_high'],
            'low': df['price_low'],
            'close': df['price_close'],
            'type': 'candlestick',
            'name': ticker,
        }
    return candlestick

