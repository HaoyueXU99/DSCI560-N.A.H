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
    
    db = DBStore()

    while True:

        menu_items = [
            "Portfolio Management Menu:",
            "1. Load portfolio from Database",
            "2. Add ticker to portfolio ",
            "3. Remove ticker from portfolio",
            "4. Display current portfolio",
            "5. Finish managing portfolio", 
        ]

        # calculate the length of the longest menu item
        max_length = max(len(item) for item in menu_items)
        # print top border
        print()
        print("#" * (max_length + 4))
        # print menu items
        for item in menu_items:
            print(f"# {item.ljust(max_length)} #")
        # print bottom border
        print("#" * (max_length + 4))

        choice = input("Enter your choice: ")

        if choice == "1":
            portfolios = db.get_all_portfolios()
            if not portfolios:
                print("No portfolios found in the database!")
                continue

            print("\nAvailable Portfolios:")
            for idx, (id, creation_date, tickers) in enumerate(portfolios):
                print(f"{idx + 1}. Created on {creation_date} with tickers: {tickers}")
            selected = int(input("Select a portfolio by number: ")) - 1

            if 0 <= selected < len(portfolios):
                _, _, tickers_string = portfolios[selected]
                tickers = tickers_string.split(',')
                portfolio.selected_tickers = tickers
                print("\n> Portfolio loaded!")
            else:
                print("\n> Invalid selection!")

        elif choice == "2":
            ticker = input("Enter the ticker you want to add: ").upper()
            portfolio.add_ticker(ticker)
        elif choice == "3":
            ticker = input("Enter the ticker you want to remove: ").upper()
            portfolio.remove_ticker(ticker)

        elif choice == "4":
            portfolio.display_portfolio()
        elif choice == "5":
            if not portfolio.get_selected_tickers():
                print("\n> Your portfolio is currently empty. Please add at least one ticker before continuing.")
            else:
                break
        else:
            print("\n> Invalid choice. Try again.")


def save_or_load_portfolio(user_portfolio):
    db = DBStore()
    print("\nPortfolio Options:")
    print("1. Save current portfolio to database")
    print("2. Continue without saving/loading")
    choice = input("Enter your choice: ")

    if choice == "1":
        db.save_portfolio(user_portfolio)
    elif choice == "2":
        pass
    else:
        print("\n> Invalid choice. Continuing without saving/loading.")

    db.close()


def main():
    api = YahooFinanceAPI()
    user_portfolio = None
    db = DBStore()

    # Interact with user to manage their portfolio
    create_own = input("Do you want to create your own portfolio? (yes/no): ").lower()
    if create_own == "yes":
        user_portfolio = UserPortfolio()
        manage_portfolio(user_portfolio)

        # After user created portfolio
        save_or_load_portfolio(user_portfolio)

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

    # Save raw data to database
    db.save_raw_data(raw_data)
    db.close()

    processor = DataProcessor(raw_data)
    processed_data = processor.process_data()
    processor.visualize_data()

    # Save processed data to CSV
    processed_csv_store = CSVStore("processed_output.csv")
    processed_csv_store.save(processed_data)


if __name__ == "__main__":
    main()