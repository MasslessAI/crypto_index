from cqt.strats.strategy import Strategy
from cqt.analyze.signal_double_dip import signal_double_dip as sdd


class StrategyDoubleDip(Strategy):
    def apply_event_logic(self, time, ledger):
        ratio = 1.0 / len(self.env.get_targets())

        for coin in self.env.get_targets():
            if self.env.has_section(coin):
                sec_coin = self.env.get_section(coin)
                ind_coin = sdd(self.env, coin, time, self.rules)
                price_coin = sec_coin.get_price_close(time)

                if ind_coin == 1:
                    ledger.buy(coin, price_coin, ratio)
                elif ind_coin == -1:
                    ledger.sell(coin, price_coin, ratio)
                else:
                    ledger.sell(coin, price_coin, ratio)

        return ledger

