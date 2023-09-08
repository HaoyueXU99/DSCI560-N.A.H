from yahoo_finance_api import YahooFinanceAPI
from portfolio import UserPortfolio
from data_fetcher import DataFetcher
from data_processor import DataProcessor
from csv_store import CSVStore
from db_store import DBStore
import pandas as pd


def create_default_portfolio():
    default_portfolio = UserPortfolio()
    default_portfolio.add_ticker("AAPL")
    default_portfolio.add_ticker("MSFT")
    return default_portfolio

def manage_portfolio(portfolio):
    while True:
        print("\nPortfolio Management Menu:")
        print("1. Add ticker to portfolio")
        print("2. Remove ticker from portfolio")
        print("3. Display current portfolio")
        print("4. Finish managing portfolio, continue with current portfolio")
        choice = input("Enter your choice: ")

        if choice == "1":
            ticker = input("Enter the ticker you want to add: ").upper()
            portfolio.add_ticker(ticker)
        elif choice == "2":
            ticker = input("Enter the ticker you want to remove: ").upper()
            portfolio.remove_ticker(ticker)
        elif choice == "3":
            portfolio.display_portfolio()
        elif choice == "4":
            break
        else:
            print("Invalid choice. Try again.")


def save_or_load_portfolio(user_portfolio):
    db = DBStore()
    print("\nPortfolio Options:")
    print("1. Save current portfolio to database")
    print("2. Load a portfolio from database")
    print("3. Continue without saving/loading")
    choice = input("Enter your choice: ")

    if choice == "1":
        db.save_portfolio(user_portfolio)
        print("Portfolio saved to database!")
    elif choice == "2":
        portfolios = db.get_all_portfolios()
        if not portfolios:
            print("No portfolios found in the database!")
            return

        print("\nAvailable Portfolios:")
        for idx, (id, creation_date, tickers) in enumerate(portfolios):
            print(f"{idx + 1}. Created on {creation_date} with tickers: {tickers}")
        selected = int(input("Select a portfolio by number: ")) - 1

        if 0 <= selected < len(portfolios):
            _, _, tickers_string = portfolios[selected]
            tickers = tickers_string.split(',')
            user_portfolio.selected_tickers = tickers
            print("Portfolio loaded!")
        else:
            print("Invalid selection!")
    elif choice == "3":
        pass
    else:
        print("Invalid choice. Continuing without saving/loading.")

    db.close()


def main():
    api = YahooFinanceAPI()
    user_portfolio = None

    # Interact with user to manage their portfolio
    create_own = input("Do you want to create your own portfolio? (yes/no): ").lower()
    if create_own == "yes":
        user_portfolio = UserPortfolio()
        manage_portfolio(user_portfolio)

        # After user created portfolio
        # save_or_load_portfolio(user_portfolio)

    else:
        print("Using default portfolio...")
        user_portfolio = create_default_portfolio()
        
    user_portfolio.display_portfolio()

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
