from cqt.strategy.strategy import Strategy
import cqt.analysis.signal_double_dip as sdp
from cqt.analysis.signal_double_dip import signal_double_dip


class StrategyTestDoubleDip(Strategy):
    def apply_event_logic(self, time, prtf):
        btc = 'btc'
        if self.asset_model.has_component(btc):
            comp_btc = self.asset_model.get_component(btc)
            ind_btc = signal_double_dip(self.asset_model, btc, time, self.rules)
            # ind_btc = sdp.signal_double_dip(self.asset_model, btc, time, self.rules)
            price_btc = comp_btc.get_price_close(time)

            if ind_btc == 1:
                prtf.buy(btc, price_btc)
            else:
                prtf.sell(btc, price_btc)

        return prtf

