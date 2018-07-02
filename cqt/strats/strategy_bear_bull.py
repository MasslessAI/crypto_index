from cqt.strats.strategy import Strategy
from cqt.env import mkt_env


class StrategyBearBull(Strategy):
    def apply_event_logic(self, time, ledger):

        return ledger
