'''
portfolio.py:
    Handles functions related to user portfolios.
'''

from yahoo_finance_api import YahooFinanceAPI
from datetime import datetime

class UserPortfolio:
    def __init__(self):
        # Initialize portfolio with the current date and an empty list of selected tickers
        self.creation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.selected_tickers = []

    def add_ticker(self, ticker):
        # Add a stock ticker to the user's portfolio
        # First, validate the ticker using Yahoo Finance API
        api = YahooFinanceAPI()
        if api.is_valid_ticker(ticker):
            # Check if ticker is not already in the portfolio before adding
            if ticker not in self.selected_tickers:
                self.selected_tickers.append(ticker)
                print(f"\n> Successfully added {ticker} to your portfolio!")
            else:
                print(f"\n> {ticker} is already in your portfolio!")
        else:
            print(f"\n> {ticker} is an invalid stock name or currently unavailable!")

    def remove_ticker(self, ticker):
        # Remove a stock ticker from the user's portfolio
        if ticker in self.selected_tickers:
            self.selected_tickers.remove(ticker)
            print(f"\n> Successfully removed {ticker} from your portfolio!")
        else:
            print(f"\n> {ticker} is not in your portfolio!")

    def get_selected_tickers(self):
        # Return the list of selected stock tickers in the portfolio
        return self.selected_tickers

    def display_portfolio(self):
        # Display the creation date of the portfolio and its selected tickers
        print(f"\n> Creation Date: {self.creation_date}")
        print("> Selected Tickers:", ", ".join(self.selected_tickers))

