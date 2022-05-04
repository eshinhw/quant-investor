from __future__ import print_function, unicode_literals
from PyInquirer import prompt, print_json
import json
import os
from questrade import QuestradeBot
from credentials import QUANT_ACCOUNT_NUM, STANDARD_ACCOUNT_NUM
from pyfiglet import Figlet
from tabulate import tabulate
from strategies.VAA import VAA
import accounts

ACCOUNTS = accounts.load_accounts()

def print_dividends(div):
    if (div['Monthly_Dividend_Income'] == 0).all():
        print()
        print("No Dividend Received")
        print()
    else:
        div_nonzero = div[div['Monthly_Dividend_Income'] > 0]
        div_nonzero.loc["Total"] = div_nonzero.sum()
        print()
        print(tabulate(div_nonzero, headers='keys'))
        print()   

def print_output(df):
    print()
    print(tabulate(df, headers='keys'))
    print()

def main_menu():
    main_selection = [
        {
            'type': 'list',
            'name': 'main_menu',
            'message': 'Main Menu',
            'choices': ['Account Overview', 'Allocation Rebalancing', 'Exit Program']
        }
    ]

    main_selection_answer = prompt(main_selection)

    if main_selection_answer.get('main_menu') == 'Account Overview':
        accounts_questions = [
            {
                'type': 'list',
                'name': 'account',
                'message': 'Account Options',
                'choices': list(ACCOUNTS.keys()) + ['Add New Account', 'Reset Saved Accounts', 'Exit Program']
            }
        ]

        accounts_answer = prompt(accounts_questions)

        if accounts_answer.get('account') == 'Add New Account':
            accounts.add_new_account()
        
        elif accounts_answer.get('account') == 'Reset Saved Accounts':
            os.remove('./accounts.json')
        
        elif accounts_answer.get('account') == 'Exit Program':
            quit()

        else:
            acct_name = accounts_answer.get('account')
            acctNum = ACCOUNTS[acct_name]
            qb = QuestradeBot(acctNum)
            account_summary(qb)
         
    elif main_selection_answer.get('main_menu') == 'Allocation Rebalancing':
        rebalance_strategy()            
    
    elif main_selection_answer.get('main_menu') == 'Exit Program':
        quit()


def account_summary(qb):
    while True:
        summary = [
            {
                'type': 'list',
                'name': 'operation',
                'message': 'Select Operation',
                'choices': [
                    'Balance Summary', 
                    'Investment Summary',
                    'Portfolio Performance',
                    'Historical Dividends', 
                    'Go to Main Menu',
                    'Exit Program'
                ]
            }
        ]

        summary_answers = prompt(summary)

        if summary_answers.get('operation') == 'Balance Summary':
            bal = qb.get_account_balance_summary()
            print_output(bal)

        elif summary_answers.get('operation') == 'Investment Summary':
            invest = qb.get_investment_summary()
            print_output(invest)

        elif summary_answers.get('operation') == 'Portfolio Performance':
            ret = qb.calculate_portfolio_performance()
            print_output(ret)

        elif summary_answers.get('operation') == 'Historical Dividends':
            div_questions = [
                {
                    'type': 'list',
                    'name': 'div_period',
                    'message': 'Choose Period',
                    'choices': ['Past 3 Months', 'Past 6 Months', 'Past 1 Year', 'Past 3 Years', 'Past 10 Years']
                }
            ]
            div_answers = prompt(div_questions)                
                
            if div_answers.get('div_period') == 'Past 3 Months':
                div = qb.get_historical_dividend_income(90)
                print_dividends(div)
                
            elif div_answers.get('div_period') == 'Past 6 Months':
                div = qb.get_historical_dividend_income(180)
                print_dividends(div)
                
            elif div_answers.get('div_period') == 'Past 1 Year':
                div = qb.get_historical_dividend_income(365)
                print_dividends(div)
                
            elif div_answers.get('div_period') == 'Past 3 Years':
                div = qb.get_historical_dividend_income(1095)
                print_dividends(div)

            elif div_answers.get('div_period') == 'Past 10 Years':
                div = qb.get_historical_dividend_income(3650)
                print_dividends(div)              

        elif summary_answers.get('operation') == 'Go to Main Menu':
            break             
        elif summary_answers.get('operation') == 'Exit Program':
            quit()

    main_menu()            

def rebalance_strategy():

    while True:
        strategy_questions = {
            'type': 'list',
            'name': 'strategy_type',
            'message': 'Select Allocation Strategy',
            'choices': [
                {'name': 'Vigilant Asset Allocation (VAA)'},
                {'name': 'Lethargic Asset Allocation (LAA)'},
                {'name': 'Go to Main Menu'}
            ]
        }

        strategy_answer = prompt(strategy_questions)

        if strategy_answer.get('strategy_type') == 'Vigilant Asset Allocation (VAA)':
            vaa = VAA()
            decision = vaa.decision()
            print(f"Invest in {decision}")
        
        elif strategy_answer.get('strategy_type') == 'Lethargic Asset Allocation (LAA)':
            vaa = VAA()
            if vaa.decision() == "QQQ":
                print({'IWD': 0.25, 'IEF': 0.25, 'GLD': 0.25, 'QQQ': 0.25})
            else:
                print({'IWD': 0.25, 'IEF': 0.25, 'GLD': 0.25, 'SHY': 0.25})

        elif strategy_answer.get('strategy_type') == 'Go to Main Menu':
            break
    
    main_menu()


if __name__ == "__main__":
    os.system("clear")
    fig = Figlet(font='slant')
    print(fig.renderText("PyQuant"))
    main_menu()















