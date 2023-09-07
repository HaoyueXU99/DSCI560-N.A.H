from yahoo_finance_api import YahooFinanceAPI
from portfolio import UserPortfolio
from data_fetcher import DataFetcher
from data_processor import DataProcessor

def main():
    api = YahooFinanceAPI()
    
    # 用户创建自己的投资组合
    user_portfolio = UserPortfolio()
    user_portfolio.add_ticker("AAPL")
    user_portfolio.add_ticker("MSFT")
    
    fetcher = DataFetcher(api, user_portfolio)
    data = fetcher.fetch_user_portfolio_data()
    
    processor = DataProcessor(data)
    processed_data = processor.process_data()
    processor.visualize_data()

if __name__ == "__main__":
    main()
