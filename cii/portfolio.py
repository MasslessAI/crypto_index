import cii
from cii import model
from datetime import timedelta
import sys


def error(msg):
    print(msg)
    sys.exit(64)


class Portfolio(object):
    def __init__(self, asset_holdings, cash):
        self.asset_holdings = asset_holdings
        self.cash = cash

    def value(self, asset_prices):
        total = self.cash
        for asset in self.asset_holdings.keys():
            if asset not in asset_prices.keys():
                error('The price of ' + asset + 'is not given in the input dict.')
            total = total + self.asset_holdings[asset] * asset_prices[asset]

        return total

    def buy(self, asset, price, quantity=None):
        if quantity is None:
            quantity = int(self.cash/price/100)*100

        if asset not in self.asset_holdings.keys():
            if self.cash > price * quantity:
                self.asset_holdings[asset] = quantity
                self.cash = self.cash - price * quantity
        else:
            if self.cash > price * quantity:
                self.asset_holdings[asset] = self.asset_holdings[asset] + quantity
                self.cash = self.cash - price * quantity

    def sell(self, asset, price, quantity=None):
        if asset in self.asset_holdings.keys():
            if quantity is None:
                quantity = self.asset_holdings[asset]

            if quantity > self.asset_holdings[asset]:
                quantity = self.asset_holdings[asset]

            self.cash = self.cash + price * quantity
            self.asset_holdings[asset] = self.asset_holdings[asset] - quantity




