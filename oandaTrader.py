import os
import json
import pandas as pd
import datetime as dt
from oandapyV20 import API
from typing import List, Dict, Tuple
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.trades as trades
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.contrib.requests as requests
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
from demo_credentials import OANDA_API_KEY, VOL_BREAKOUT_ACCOUNT_ID
from oanda_new import Oanda

class OandaTrader(Oanda):

    def __init__(self, api_key, accountID) -> None:
        super().__init__(api_key, accountID)

    def calculate_unit_size(self,
                            symbol: str,
                            entry: float,
                            stop: float,
                            risk_per_trade: float):

        if '_USD' in symbol:
            decimal = 4
            multiple = 10000

        if '_JPY' in symbol:
            decimal = 2
            multiple = 100

        account_balance = self.get_balance(self.acctID)
        risk_amt_per_trade = account_balance * risk_per_trade
        entry = round(entry, decimal)
        stop = round(stop, decimal)
        stop_loss_pips = round(abs(entry - stop) * multiple, 0)

        if '_USD' in symbol:
            (currentAsk, currentBid) = self.get_current_ask_bid_price(symbol)
            acct_conversion_rate = 1 / ((currentAsk + currentBid) / 2)
            unit_size = round((risk_amt_per_trade / stop_loss_pips *
                            acct_conversion_rate) * multiple, 0)
            return unit_size

        if '_JPY' in symbol:
            (currentAsk, currentBid) = self.get_current_ask_bid_price(symbol)
            acct_conversion_rate = ((currentAsk + currentBid) / 2)
            unit_size = round((risk_amt_per_trade / stop_loss_pips *
                            acct_conversion_rate) * multiple, 0)
            return unit_size


    def update_order_trade_status(self):
        trade_list = self.get_trade_list(account_ID)
        order_list = get_order_list(account_ID)

        for trade in trade_list:
            for order in order_list:
                if order["type"] == "LIMIT" and trade["instrument"] == order["instrument"]:
                    cancel_single_order(account_ID, order["id"])


    def get_order_details(account_ID: str, order_ID: str) -> Dict:
        r = orders.OrderDetails(accountID=account_ID, orderID=order_ID)
        resp = client.request(r)
        return (resp['order'])


    def find_order_id(account_ID: str, symbol: str, direction: str) -> str:
        order_list = get_order_list(account_ID)

        for order in order_list:
            if direction == 'LONG':
                if order['type'] == 'LIMIT' and order['instrument'] == symbol and not ('-' in order['units']):
                    return order['id']
            if direction == 'SHORT':
                if order['type'] == 'LIMIT' and order['instrument'] == symbol and ('-' in order['units']):
                    return order['id']


    def check_open_order(account_ID: str, symbol: str):
        order_list = get_order_list(account_ID)
        for order in order_list:
            if order["type"] == "LIMIT" and order["instrument"] == symbol:
                return True
        return False


    def check_open_trade(account_ID: str, symbol: str):
        trade_list = get_trade_list(account_ID)
        for trade in trade_list:
            if trade["instrument"] == symbol:
                return True
        return False


    def cancel_single_order(self, account_ID: str, order_ID: str) -> None:
        r = orders.OrderCancel(accountID=self.acctID, orderID=order_ID)
        self.client.request(r)


    def close_all_trades(self) -> None:
        trades_list = self.get_trade_list()
        for trade in trades_list:
            r = trades.TradeClose(accountID=self.acctID, tradeID=trade["id"])
            self.client.request(r)


    def cancel_all_orders(self) -> None:
        order_list = self.get_order_list()
        for order in order_list:
            r = orders.OrderCancel(accountID=self.acctID, orderID=order["id"])
            self.client.request(r)


    def get_order_list(self) -> List[Dict]:
        """ Retrieve a list of open orders
        """
        r = orders.OrderList(self.acctID)
        resp = self.client.request(r)
        return resp["orders"]


    def get_trade_list(self) -> List[Dict]:
        """ Retrieve a list of open trades
        """
        r = trades.TradesList(self.acctID)
        resp = self.client.request(r)
        return resp["trades"]




if __name__ == '__main__':

    ot = OandaTrader(OANDA_API_KEY, VOL_BREAKOUT_ACCOUNT_ID)
    print(ot.calculate_MA('EUR_USD', 20, 'D'))
