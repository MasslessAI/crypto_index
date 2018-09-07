import sys
sys.path.append('/home/ec2-user/crypto_index/')
#sys.path.append('/home/ec2-user/crypto_index/notebooks/')

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
plt.switch_backend('agg')
import copy
import cqt.strats.StrategyTensorFlow as stg_tf

def main():
    outDir = '/home/ec2-user/performance_tracking'
    TODAY = datetime.now()
    BACK_TEST_START_DATE = datetime(2018,1,1)
    tbl_name='coinapi-ohlcv-COINBASE_SPOT_BTC_USD-1DAY'
    df_btc=db.get_from_db(tbl_name,from_date='2017-10-01',to_date=TODAY.strftime('%Y-%M-%d'))
    config = {'asset_type': 'spot'}
    model_btc_eth = env.MktEnv([])
    comp_btc = envspot.MktEnvSpot('btc', df_btc.get_index_data(), config)
    model_btc_eth.insert_section(comp_btc)



    cash = 10000
    assets = {'btc': 0}
    ini_pfo = ledger.Ledger(assets, cash)


    ls_rule = {'method' : 'moving_average', 'window_size' : [3, 5], 'tolerance_up' : 0.03, 'tolerance_down' : 0.03}
    strats = stg_tf.StrategyTensorFlow(model_btc_eth, ini_pfo, ls_rule, '/home/ec2-user/crypto_index/notebooks/69-model.json', '/home/ec2-user/crypto_index/notebooks/69-model.h5', '/home/ec2-user/crypto_index/notebooks/scaler.pkl')

    report = strats.back_testing(BACK_TEST_START_DATE)
    strategyName = 'RL'+TODAY.strftime('%Y%m%d')
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
    fig.savefig(os.path.join(outDir, strategyName+'.pdf'))
if __name__ == '__main__':
    main()    
