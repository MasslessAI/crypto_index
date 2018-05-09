from cqt.strategy.strategy import Strategy


class StrategyBearBull(Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        eth = 'eth'
        if self.asset_model.has_component(btc) and self.asset_model.has_component(eth):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = comp_btc.signal_bear_or_bull(time, self.rules)
            price_btc = comp_btc.get_price_close(time)

            comp_eth = self.asset_model.get_component(eth)
            ind_eth = comp_eth.signal_bear_or_bull(time, self.rules)
            price_eth = comp_eth.get_price(time)

            if ind_btc == -1 and ind_eth == -1:
                prtf.sell_unit(btc, price_btc)
                prtf.sell_unit(eth, price_eth)
            elif ind_btc == -1 and ind_eth == 1:
                prtf.buy(eth, price_eth)
            elif ind_btc == 1 and ind_eth == -1:
                prtf.buy(btc, price_btc)
            elif ind_btc == 1 and ind_eth == 1:
                prtf.buy(btc, price_btc, 0.25)
                prtf.buy(eth, price_eth, 0.25)

        return prtf
