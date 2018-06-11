import sys

from datetime import datetime, timedelta

sys.path.append('../')
import cii
import cii.datagen as dg
import cii.model as md
import cii.portfolio as pfo
import cii.strategy as stg
import pandas as pd



class StrategyTest1(stg.Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        eth = 'eth'
        if self.asset_model.has_component(btc) and self.asset_model.has_component(eth):
            prev_time = time - timedelta(days=1)
            
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = comp_btc.bear_or_bull(time, self.rules)
            int_btc_prev = comp_btc.bear_or_bull(prev_time, self.rules)
            price_btc = comp_btc.get_price(time)

            comp_eth = self.asset_model.get_component(eth)
            ind_eth = comp_eth.bear_or_bull(time, self.rules)
            int_eth_prev = comp_eth.bear_or_bull(prev_time, self.rules)
            price_eth = comp_eth.get_price(time)

            if ind_btc == 1 and ind_eth == 1:
                prtf.buy(btc, price_btc, 0.5)
                prtf.buy(eth, price_eth, prtf.cash)
            elif ind_btc == 1 and ind_eth == 0:
                prtf.buy(btc, price_btc, 1.0)
            elif ind_btc == 1 and ind_eth == -1:
                prtf.sell_unit(eth, price_eth)
                prtf.buy(btc, price_btc, 0.25)
            elif ind_btc == -1:
                prtf.sell_unit(btc, price_btc)
                prtf.sell_unit(eth, price_eth)

#             print(ind_btc, ind_eth)
            if prtf.value(self.asset_model.get_prices(time)) > 1.1 * self.initial_portfolio.value(self.asset_model.get_prices(time)):
                prtf.set_aside(0.05 * prtf.value(self.asset_model.get_prices(time)))
#                 print(prtf.value(asset_model.get_prices(time)))
#                 print(self.initial_portfolio.value(asset_model.get_prices(time)))
#                 print('Give it to me!' )
#                 print(time)
                
        return prtf

class StrategyTest2(stg.Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_component(btc):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = comp_btc.average_comparison(time, self.rules)
            price_btc = comp_btc.get_price(time)

            if ind_btc == -1:
                prtf.sell_unit(btc, price_btc)
            elif ind_btc == 1:
                prtf.buy(btc, price_btc, 1)     
            else:
                pass

        return prtf

class StrategyTest3(stg.Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        eth = 'eth'
        if self.asset_model.has_component(btc) and self.asset_model.has_component(eth):
            p_time = time - timedelta(days=3)
            pp_time = time - timedelta(days=6)
            
            comp_btc = self.asset_model.get_component(btc)
#            ind_btc = comp_btc.bear_or_bull(time, self.rules)
#             ind_btc_after = comp_btc.bear_or_bull(after_time, self.rules)
            price_btc = comp_btc.get_price(time)
            price_btc_p = comp_btc.get_price(p_time)
            price_btc_pp = comp_btc.get_price(pp_time)
            
            cvx = (price_btc - price_btc_p) - (price_btc_p - price_btc_pp)
#             comp_eth = self.asset_model.get_component(eth)
#             ind_eth = comp_eth.bear_or_bull(time, self.rules)
#             ind_eth_prev = comp_eth.bear_or_bull(prev_time, self.rules)
#             price_eth = comp_eth.get_price(time)

#             if ind_btc_prev == -1 and ind_btc == 1:
#                 prtf.buy(btc, price_btc, 1.0)
#             elif ind_btc_prev == -1 and ind_btc == 0:
#                 prtf.buy(btc, price_btc, 0.2)
#             elif ind_btc_prev == 1 and ind_btc != 1:
#                 prtf.sell(btc, price_btc, 0.8)
#             elif ind_btc_prev == 1 and ind_btc == 1:
#                 prtf.buy(btc, price_btc, 0.5)

            if cvx > 0:
                prtf.buy(btc, price_btc, 1.0)
            else:
                prtf.sell(btc, price_btc, 1.0)

#             if prtf.value(asset_model.get_prices(time)) > 1.1 * self.initial_portfolio.value(asset_model.get_prices(time)):
#                 prtf.set_aside(0.05 * prtf.value(asset_model.get_prices(time)))
#                 print(prtf.value(asset_model.get_prices(time)))
#                 print(self.initial_portfolio.value(asset_model.get_prices(time)))
#                 print('Give it to me!' )
#                 print(time)
                
        return prtf

strategyMetaDict = {
    'strategyTest1': StrategyTest1,
}