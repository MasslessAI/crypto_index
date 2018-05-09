from cqt.strategy.strategy import Strategy


class StrategyLongShortAverage(Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_component(btc):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = comp_btc.signal_long_short_average(time, self.rules)
            price_btc = comp_btc.get_price_close(time)

            if ind_btc == -1:
                prtf.sell_unit(btc, price_btc)
            elif ind_btc == 1:
                prtf.buy(btc, price_btc, 1)
            else:
                pass

        return prtf
