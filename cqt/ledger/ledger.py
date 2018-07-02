import cqt
from cqt.error_msg import error
from datetime import timedelta
import sys


class Ledger(object):
    def __init__(self, holdings, cash):
        self.holdings = holdings
        self.cash = cash
        self.wife_pocket = 0.0

    def value(self, asset_prices):
        total = self.cash + self.wife_pocket
        for asset in self.holdings.keys():
            if asset not in asset_prices.keys():
                error('The price of ' + asset + 'is not given in the input dict.')
            total = total + self.holdings[asset] * asset_prices[asset]

        return total

    def buy(self, asset, price, percent=None):
        if percent is None or percent > 1:
            percent = 1
        elif percent < 0:
            percent = 0

        if asset not in self.holdings.keys():
            self.holdings[asset] = self.cash * percent / price
        else:
            self.holdings[asset] = self.holdings[asset] + self.cash * percent / price

        self.cash = self.cash * (1 - percent)

    def buy_unit(self, asset, price, quantity=None):
        if quantity is None:
            quantity = self.cash / price

        if asset not in self.holdings.keys():
            if self.cash > price * quantity:
                self.holdings[asset] = quantity
                self.cash = self.cash - price * quantity
        else:
            if self.cash > price * quantity:
                self.holdings[asset] = self.holdings[asset] + quantity
                self.cash = self.cash - price * quantity

    def sell(self, asset, price, percent=None):
        if percent is None or percent > 1:
            percent = 1
        elif percent < 0:
            percent = 0

        if asset in self.holdings.keys():
            self.cash = self.cash + price * self.holdings[asset] * percent
            self.holdings[asset] = self.holdings[asset] * (1 - percent)

    def sell_unit(self, asset, price, quantity=None):
        if asset in self.holdings.keys():
            if quantity is None:
                quantity = self.holdings[asset]

            if quantity > self.holdings[asset]:
                quantity = self.holdings[asset]

            self.cash = self.cash + price * quantity
            self.holdings[asset] = self.holdings[asset] - quantity

    def set_aside(self, amount):
        if amount > self.cash:
            amount = self.cash

        self.wife_pocket = self.wife_pocket + amount
        self.cash = self.cash - amount





