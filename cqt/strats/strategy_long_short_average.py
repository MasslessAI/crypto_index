from cqt.strats.strategy import Strategy
from cqt.analyze.signal_long_short_crossing import signal_long_short_crossing as slsc
from cqt.analyze.signal_long_short_crossing import signal_average_envelope as sae


class StrategySimpleMA(Strategy):
    def apply_event_logic(self, time, ledger):
        coin = 'btc'
        if self.env.has_section(coin):
            section_coin = self.env.get_section(coin)
            ind_coin = slsc(self.env, coin, time, self.rules)
            price_coin = section_coin.get_price_close(time)

            if ind_coin == -1:
                ledger.sell_unit(coin, price_coin)
            elif ind_coin == 1:
                ledger.buy(coin, price_coin)
            else:
                pass

        return ledger


class StrategyInverseMA(Strategy):
    def apply_event_logic(self, time, ledger):
        coin = 'btc'
        if self.env.has_section(coin):
            section_coin = self.env.get_section(coin)
            ind_coin = slsc(self.env, coin, time, self.rules)
            price_coin = section_coin.get_price_close(time)

            if ind_coin == 1:
                ledger.sell_unit(coin, price_coin)
            elif ind_coin == -1:
                ledger.buy(coin, price_coin)
            else:
                pass

        return ledger


class StrategyBlendMA(Strategy):
    def apply_event_logic(self, time, ledger):
        coin = 'btc'

        if self.env.has_section(coin):
            rules_short = self.rules.copy()
            rules_short['window_size'] = [rules_short['window_size'][0], rules_short['window_size'][1]]
            rules_long = self.rules.copy()
            rules_long['window_size'] = [rules_long['window_size'][2], rules_long['window_size'][3]]

            ind_coin_long = slsc(self.env, coin, time, rules_long)
            ind_coin_short = slsc(self.env, coin, time, rules_short)
            strats_long = StrategySimpleMA(self.env, ledger, rules_long)
            strats_short = StrategySimpleMA(self.env, ledger, rules_short)

            if ind_coin_long == 1:
                ledger = strats_long.apply_event_logic(time, ledger)
            elif ind_coin_short == -1:
                ledger = strats_short.apply_event_logic(time, ledger)
            else:
                pass

        return ledger
