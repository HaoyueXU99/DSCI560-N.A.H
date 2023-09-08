'''
portfolio.py:
    Handles functions related to user portfolios.
'''

from datetime import datetime

class UserPortfolio:
    def __init__(self):
        self.creation_date = datetime.now().strftime('%Y-%m-%d')
        self.selected_tickers = []

    def add_ticker(self, ticker):
        self.selected_tickers.append(ticker)

    def remove_ticker(self, ticker):
        if ticker in self.selected_tickers:
            self.selected_tickers.remove(ticker)

    def get_selected_tickers(self):
        return self.selected_tickers

    def display_portfolio(self):
        print(f"Creation Date: {self.creation_date}")
        print("Selected Tickers:", ", ".join(self.selected_tickers))
