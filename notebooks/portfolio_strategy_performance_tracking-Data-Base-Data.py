
# coding: utf-8

# In[36]:

import sys
sys.path.append('../')

import os

import cqt
import cqt.env.mkt_env as env 
import cqt.env.mkt_env_spot as envspot
import cqt.ledger.ledger as ledger
import cqt.datagen as dg
import cqt.dbutility.dbutility as db
import cqt.strats.strategy as stg
import cqt.strats.strategy_long_short_average as stg_ls
import pandas as pd
import pickle

from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import copy
import cqt.strats.StrategyTensorFlow as stg_tf


# In[37]:

os.listdir('../data/pickle')

import pandas as pd
df_btc = pd.read_csv('../data/coinapi_ohlcv_BITSTAMP_SPOT_BTC_USD_1HRS_data.csv')


### db.get_table_list() method takes 1 argument db_id, and is defaulted to 'Amazon_RDS'
df_tbl_list=db.get_table_list()
print(df_tbl_list)


# In[38]:

TODAY = datetime.now()

tbl_name='coinapi-ohlcv-COINBASE_SPOT_BTC_USD-1DAY'
df_btc=db.get_from_db(tbl_name,from_date='2015-01-01',to_date='2017-01-01')
#df_eth = db.get_from_db("coinapi-ohlcv-COINBASE_SPOT_ETH_USD-1DAY",from_date='2016-01-01',to_date=TODAY.strftime('%Y-%M-%d'))
df_btc.data


# In[39]:

#df_btc.data = pd.read_csv('../data/coinapi_ohlcv_BITSTAMP_SPOT_BTC_USD_1HRS_data.csv')
print(df_btc.type)
print(df_btc.source)
print(df_btc.period)
print(df_btc.symbol)
#df_btc.data

df_btc.period = '1HRS'

print(df_btc.fromTime)
print(df_btc.toTime)
print(df_btc.data.keys())

print(df_btc.get_index_data())

index_data = df_btc.get_index_data()
index_data.data = pd.read_csv('../data/coinapi_ohlcv_BITSTAMP_SPOT_BTC_USD_1HRS_data.csv')
#df_btc.data = pd.read_csv('../data/coinapi_ohlcv_BITSTAMP_SPOT_BTC_USD_1HRS_data.csv')

index_data.validate()

#df_btc.data.key.sort_values().iloc[0]
#df_btc.data.key.sort_values().iloc[-1]


# In[40]:

config = {'asset_type': 'spot'}
model_btc_eth = env.MktEnv([])
comp_btc = envspot.MktEnvSpot('btc', index_data, config)
model_btc_eth.insert_section(comp_btc)



cash = 10000
assets = {'btc': 0}
ini_pfo = ledger.Ledger(assets, cash)


# In[41]:

# Long/Short Average
ls_rule = {'method' : 'moving_average', 'window_size' : [15, 30], 'tolerance_up' : 0.03, 'tolerance_down' : 0.03}
strats = stg_ls.StrategyInverseMA(model_btc_eth, ini_pfo, ls_rule)
start_date_str = '2016-01-01'
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
report = strats.back_testing(None)

longShortReport = report.copy()


# In[42]:

longShortReport[-10:]


# In[43]:

report = longShortReport
outDir='./'

strategyName = '2016-2017 Inverse Long Short Average [15, 30] (0.03, 0.03)'
report.to_csv(os.path.join(outDir, strategyName+'.csv'), index=False)
fig_width = 12
fig_height = 12
fig, ax0 = plt.subplots(2,1, figsize=(fig_width,fig_height))
ax0[0].plot(report['date'], report['total'])
ax0[0].plot(report['date'], report['btc_price'] * cash / report['btc_price'][0])
ax0[0].set_title('portfolio performance')
ax0[1].plot(report['date'], report['pnl'])
ax0[1].set_title('daily pnl')
fig.suptitle(strategyName)
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
plt.show()

print('max daily gain:', report['pnl'].max())
print('max daily loss:', report['pnl'].min())


# In[46]:

import cqt.strats.strategy_double_dip as stg_dd

# Double Dip Strategy
dd_rule = {'method' : 'moving_average', 'window_size' : [3, 5], 'tolerance_up' : 0.03, 'tolerance_down' : 0.03}
strats = stg_dd.StrategyDoubleDip(model_btc_eth, ini_pfo, dd_rule)
start_date_str = '2016-01-01'
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
report = strats.back_testing(None)


# In[26]:

strategyName = '2016-2017 Double Tops Bottoms [3, 5] (0.03, 0.03)'
report.to_csv(os.path.join(outDir, strategyName+'.csv'), index=False)
fig_width = 12
fig_height = 12
fig, ax0 = plt.subplots(2,1, figsize=(fig_width,fig_height))
ax0[0].plot(report['date'], report['total'])
ax0[0].plot(report['date'], report['btc_price'] * cash / report['btc_price'][0])
ax0[0].set_title('portfolio performance')
ax0[1].plot(report['date'], report['pnl'])
ax0[1].set_title('daily pnl')
fig.suptitle(strategyName)
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
plt.show()

print('max daily gain:', report['pnl'].max())
print('max daily loss:', report['pnl'].min())


# In[17]:




# In[27]:

from talib.abstract import *
import copy
prices = copy.deepcopy(comp_btc.data)
prices.rename(columns={'price_open': 'open', 'price_high': 'high', 'price_low': 'low', 'price_close': 'close', 'volume_traded': 'volume'}, inplace=True)
close = prices['close'].values
sma15 = SMA(prices, timeperiod=15)
sma60 = SMA(prices, timeperiod=60)
rsi = RSI(prices, timeperiod=14)
atr = ATR(prices, timeperiod=14)


# In[35]:

prices.index[-100:]


# In[28]:

import numpy
import talib

close = prices['close'].values

from talib import MA_Type

upper, middle, lower = talib.BBANDS(close, matype=MA_Type.T3)


# In[39]:

fig_width = 12
fig_height = 6
fig, ax0 = plt.subplots(1,1, figsize=(fig_width,fig_height))
ax0.plot(prices.index[-100:],close[-100:],  'r--',prices.index[-100:],upper[-100:],'b--',prices.index[-100:],middle[-100:], 'y--', prices.index[-100:],lower[-100:], 'g--')
plt.show()


# In[40]:

import cqt.strats.StrategyBBANDS as stg_bb

# B BANDS Strategy
dd_rule = {'method' : 'moving_average', 'window_size' : [3, 5], 'tolerance_up' : 0.03, 'tolerance_down' : 0.03}
strats = stg_bb.StrategyBBANDS(model_btc_eth, ini_pfo, dd_rule)
start_date_str = '2016-01-01'
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
report = strats.back_testing(start_date)


# In[41]:

plt.plot(report['date'],report['total'])


# In[42]:

strategyName = '2016-2017 Bollinger Bands Strategy [2, 2] (14,MA_Type.T3)'
report.to_csv(os.path.join(outDir, strategyName+'.csv'), index=False)
fig_width = 12
fig_height = 12
fig, ax0 = plt.subplots(2,1, figsize=(fig_width,fig_height))
ax0[0].plot(report['date'], report['total'])
ax0[0].plot(report['date'], report['btc_price'] * cash / report['btc_price'][0])
ax0[0].set_title('portfolio performance')
ax0[1].plot(report['date'], report['pnl'])
ax0[1].set_title('daily pnl')
fig.suptitle(strategyName)
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
plt.show()

print('max daily gain:', report['pnl'].max())
print('max daily loss:', report['pnl'].min())


# In[43]:

import cqt.strats.StrategyRSI as stg_rsi

# RSI Strategy
rsi_rule = {'method' : 'RSI'}
strats = stg_rsi.StrategyRSI(model_btc_eth, ini_pfo, rsi_rule)
start_date_str = '2016-01-01'
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
report = strats.back_testing(start_date)


# In[44]:

strategyName = '2016-2017 Relative Strength Index Strategy [30, 70]'
report.to_csv(os.path.join(outDir, strategyName+'.csv'), index=False)
fig_width = 12
fig_height = 12
fig, ax0 = plt.subplots(2,1, figsize=(fig_width,fig_height))
ax0[0].plot(report['date'], report['total'])
ax0[0].plot(report['date'], report['btc_price'] * cash / report['btc_price'][0])
ax0[0].set_title('portfolio performance')
ax0[1].plot(report['date'], report['pnl'])
ax0[1].set_title('daily pnl')
fig.suptitle(strategyName)
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
plt.show()

print('max daily gain:', report['pnl'].max())
print('max daily loss:', report['pnl'].min())


# In[46]:

report[-10:]


# In[48]:

import cqt.strats.StrategyATR as stg_atr

# ATR Strategy
atr_rule = {'method' : 'ATR','bandwidth':[-2,2]}
strats = stg_atr.StrategyATR(model_btc_eth, ini_pfo, atr_rule)
start_date_str = '2016-01-01'
start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
report = strats.back_testing(start_date)


# In[49]:

strategyName = '2016-2017 ATR Strategy [-2, 2]'
report.to_csv(os.path.join(outDir, strategyName+'.csv'), index=False)
fig_width = 12
fig_height = 12
fig, ax0 = plt.subplots(2,1, figsize=(fig_width,fig_height))
ax0[0].plot(report['date'], report['total'])
ax0[0].plot(report['date'], report['btc_price'] * cash / report['btc_price'][0])
ax0[0].set_title('portfolio performance')
ax0[1].plot(report['date'], report['pnl'])
ax0[1].set_title('daily pnl')
fig.suptitle(strategyName)
plt.tight_layout(rect=[0, 0.03, 1, 0.97])
fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
plt.show()

print('max daily gain:', report['pnl'].max())
print('max daily loss:', report['pnl'].min())

