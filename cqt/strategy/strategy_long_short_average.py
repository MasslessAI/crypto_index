from cqt.strategy.strategy import Strategy
from cqt.analysis.signal_long_short_crossing import signal_long_short_average, signal_average_envelope
from cqt.analysis.signal_consecutive_moves import signal_consecutive_moves

class StrategyLongShortAverage(Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_component(btc):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = signal_long_short_average(self.asset_model, btc, time, self.rules )
            # ind_btc = comp_btc.signal_long_short_average(time, self.rules)
            price_btc = comp_btc.get_price_close(time)

            if ind_btc == -1:
                prtf.sell_unit(btc, price_btc)
            elif ind_btc == 1:
                prtf.buy(btc, price_btc, 1)
            else:
                pass

        return prtf

class StrategyInverseLongShortAverage(Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_component(btc):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = signal_long_short_average(self.asset_model, btc, time, self.rules )
            # ind_btc = comp_btc.signal_long_short_average(time, self.rules)
            price_btc = comp_btc.get_price_close(time)

            if ind_btc == 1:
                prtf.sell_unit(btc, price_btc)
            elif ind_btc == -1:
                prtf.buy(btc, price_btc, 1)
            else:
                pass

        return prtf
