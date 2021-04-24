import os
import math
import price
import requests
import momentum
import pyticker
import dividend
import questrade
import numpy as np
import pandas as pd
import datetime as dt
import matplotlib.pyplot as plt
from qtrade import Questrade as qt
import pandas_datareader.data as web

if os.path.exists("./access_token.yml"):
    qtrade = qt(token_yaml="./access_token.yml")
    qtrade.refresh_access_token(from_yaml=True)
else:
    code = open("./credentials/questrade_access_code.txt", "r").read()
    qtrade = qt(access_code=code)

acctId = qtrade.get_account_id()

def get_balance():
    token = qtrade.access_token
    token_type = token['token_type']
    access_token = token['access_token']
    url = token['api_server'] + '/v1/accounts/' + acctId[0] + '/balances'
    bal = requests.get(url, headers={'Authorization': f'{token_type} {access_token}'}).json()
    data = {'Currency': [], 'Cash': [], 'Market_Value': [], 'Total_Equity': [], 'Cash (%)': [], 'Investment (%)': []}

    for x in bal['perCurrencyBalances']:
        data['Currency'].append(x['currency'])
        data['Cash'].append(x['cash'])
        data['Market_Value'].append(x['marketValue'])
        data['Total_Equity'].append(x['totalEquity'])
        data['Cash (%)'].append(round(100 * x['cash']/x['totalEquity'],2))
        data['Investment (%)'].append(round(100 * x['marketValue']/x['totalEquity'],2))

    df = pd.DataFrame(data)
    df.set_index('Currency', inplace=True)
    return df

def get_usd_total_equity():
    bal = get_balance()
    return bal.loc['USD','Total_Equity']

def get_cad_total_equity():
    bal = get_balance()
    return bal.loc['CAD','Total_Equity']


def get_positions():
    position_data = {
        'Symbol': [],
        'Description': [],
        'Currency': [],
        'Quantities': [],
        'Market Value': [],
        'Gain/Loss (%)': []
    }
    total_costs = 0
    total_market_value = 0
    for account in acctId:
        positions = qtrade.get_account_positions(account)
        for position in positions:
            symbol = position['symbol']
            description = qtrade.ticker_information(symbol)['description']
            qty = position['openQuantity']
            cmv = position['currentMarketValue']
            currency = qtrade.ticker_information(symbol)['currency']
            cost = position['totalCost']
            change = round(100 * (cmv - cost) / cost, 2)

            total_market_value = total_market_value + cmv
            total_costs = total_costs + cost
            position_data['Symbol'].append(symbol)
            position_data['Description'].append(description)
            position_data['Currency'].append(currency)
            position_data['Quantities'].append(qty)
            position_data['Market Value'].append(cmv)
            position_data['Gain/Loss (%)'].append(change)

    portfolio = pd.DataFrame(position_data)
    portfolio.set_index('Symbol', inplace=True)
    total_equity = get_usd_total_equity()
    portfolio['%Portfolio'] = [round(100 * (x / total_equity), 2) for x in portfolio['Market Value']]
    return portfolio

def get_dividend_income():
    startDate = '2018-04-01'
    endDate = dt.date.today().strftime("%Y-%m-%d")
    dtrange = pd.date_range(startDate, endDate, freq='d')
    months = pd.Series(dtrange.month)
    starts, ends = months.ne(months.shift(1)), months.ne(months.shift(-1))
    startEndDates = pd.DataFrame({
        'month_starting_date':
        dtrange[starts].strftime('%Y-%m-%d'),
        'month_ending_date':
        dtrange[ends].strftime('%Y-%m-%d')
    })
    dateList = startEndDates.values.tolist()

    output = {}
    total_div_earned = 0

    for date in dateList:
        start = date[0]
        end = date[1]
        activities = qtrade.get_account_activities(acctId[0], start, end)
        monthly_div = 0
        for activity in activities:
            if activity['type'] == 'Dividends':
                monthly_div = monthly_div + activity['netAmount']
        output[dt.datetime.strptime(start,
                                    "%Y-%m-%d").strftime("%Y-%m")] = monthly_div
        total_div_earned = total_div_earned + monthly_div

    monthly_div_df = pd.DataFrame.from_dict(output,
                                        orient='index',
                                        columns=['Monthly_Dividend_Income'])

    return monthly_div_df

def color_negative_red(value):

    if value < 0:
        color = 'red'
    elif value > 0:
        color = 'green'
    else:
        color = 'black'

    return 'color: %s' % color

def calculate_shares(symbol: str, weight: float):
    total_equity = get_usd_total_equity()
    amount = total_equity * weight
    curr_price = price.get_current_price(symbol)
    return (amount, math.floor(amount / curr_price))

if __name__ == '__main__':

    if os.path.exists("./access_token.yml"):
        qtrade = qt(token_yaml="./access_token.yml")
        qtrade.refresh_access_token(from_yaml=True)
    else:
        code = open("./credentials/questrade_access_code.txt", "r").read()
        qtrade = qt(access_code=code)

    acctId = qtrade.get_account_id()

    bal = get_balance()
    print(bal)

    pos = get_positions()
    print(pos)