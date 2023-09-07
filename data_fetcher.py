'''
data_fetcher.py:
    Scrap data from user portfolios.
'''
class DataFetcher:
    def __init__(self, api, portfolio):
        self.api = api
        self.portfolio = portfolio
    
    def fetch_user_portfolio_data(self):
        data = {}
        for ticker in self.portfolio.get_selected_tickers():
            data[ticker] = self.api.fetch_data(ticker)
        return data
