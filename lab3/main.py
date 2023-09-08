from yahoo_finance_api import YahooFinanceAPI
from portfolio import UserPortfolio
from data_fetcher import DataFetcher
from data_processor import DataProcessor
from csv_store import CSVStore
from db_store import DBStore
import pandas as pd

def main():
    api = YahooFinanceAPI()
    user_portfolio = UserPortfolio()
    user_portfolio.add_ticker("AAPL")
    user_portfolio.add_ticker("MSFT")
    
    fetcher = DataFetcher(api, user_portfolio)
    data = fetcher.fetch_user_portfolio_data()
    raw_data = pd.concat(data.values())

    # Save raw data to CSV
    raw_csv_store = CSVStore("raw_output.csv")
    raw_csv_store.save(raw_data)
    
    processor = DataProcessor(raw_data)
    processed_data = processor.process_data()
    processor.visualize_data()

    # Save processed data to CSV
    processed_csv_store = CSVStore("processed_output.csv")
    processed_csv_store.save(processed_data)

    # Save to Database
    to_db = DBStore()
    to_db.save()
    to_db.close()

if __name__ == "__main__":
    main()
