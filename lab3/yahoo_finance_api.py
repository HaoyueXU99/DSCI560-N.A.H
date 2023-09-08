'''
yahoo_finance_api.py:
    Implement the interface defined in api_interface.py.
'''
import yfinance as yf
from api_interface import DataAPIInterface

class YahooFinanceAPI(DataAPIInterface):
    def fetch_data(self, ticker, range="1y"):
        data = yf.download(ticker, period=range)
        data['Ticker'] = ticker
        return data

    def is_valid_ticker(self, ticker):
            try:
                stock = yf.Ticker(ticker)
                if stock.history(period="1d").empty:
                    return False
                return True
            except:
                return False