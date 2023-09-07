'''
portfolio.py:
    Handles functions related to user portfolios.
'''

class UserPortfolio:
    def __init__(self):
        self.selected_tickers = []
    
    def add_ticker(self, ticker):
        self.selected_tickers.append(ticker)
    
    def remove_ticker(self, ticker):
        if ticker in self.selected_tickers:
            self.selected_tickers.remove(ticker)

    def get_selected_tickers(self):
        return self.selected_tickers
