import cqt
from cqt import model
from datetime import timedelta
import sys


def error(msg):
    print(msg)
    sys.exit(64)


class Portfolio(object):
    def __init__(self, asset_holdings, cash):
        self.asset_holdings = asset_holdings
        self.cash = cash
        self.wife_pocket = 0.0

    def value(self, asset_prices):
        total = self.cash + self.wife_pocket
        for asset in self.asset_holdings.keys():
            if asset not in asset_prices.keys():
                error('The price of ' + asset + 'is not given in the input dict.')
            total = total + self.asset_holdings[asset] * asset_prices[asset]

        return total

    def buy(self, asset, price, percent=None):
        if percent is None or percent > 1:
            percent = 1
        elif percent < 0:
            percent = 0

        if asset not in self.asset_holdings.keys():
            self.asset_holdings[asset] = self.cash * percent / price
        else:
            self.asset_holdings[asset] = self.asset_holdings[asset] + self.cash * percent / price

        self.cash = self.cash * (1 - percent)

    def buy_unit(self, asset, price, quantity=None):
        if quantity is None:
            quantity = self.cash / price

        if asset not in self.asset_holdings.keys():
            if self.cash > price * quantity:
                self.asset_holdings[asset] = quantity
                self.cash = self.cash - price * quantity
        else:
            if self.cash > price * quantity:
                self.asset_holdings[asset] = self.asset_holdings[asset] + quantity
                self.cash = self.cash - price * quantity

    def sell(self, asset, price, percent=None):
        if percent is None or percent > 1:
            percent = 1
        elif percent < 0:
            percent = 0

        if asset in self.asset_holdings.keys():
            self.cash = self.cash + price * self.asset_holdings[asset] * percent
            self.asset_holdings[asset] = self.asset_holdings[asset] * (1 - percent)

    def sell_unit(self, asset, price, quantity=None):
        if asset in self.asset_holdings.keys():
            if quantity is None:
                quantity = self.asset_holdings[asset]

            if quantity > self.asset_holdings[asset]:
                quantity = self.asset_holdings[asset]

            self.cash = self.cash + price * quantity
            self.asset_holdings[asset] = self.asset_holdings[asset] - quantity

    def set_aside(self, amount):
        if amount > self.cash:
            amount = self.cash

        self.wife_pocket = self.wife_pocket + amount
        self.cash = self.cash - amount





