'''
db_store.py:
    Implement the interface defined in data_store_interface.py to support data storage to the database. 
    This class uses the mysql.connector library to connect to the MySQL database.
'''

import mysql.connector
import numpy as np

class DBStore:
    def __init__(self, host='localhost', user='Dsci560', password='Dsci560@1234', dbname='Lab3_NAH'):
        # Establishing a connection to the database
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=dbname
        )
        # Create a cursor to interact with the database
        self.cursor = self.conn.cursor(buffered=True)
        
        # Initialize the database: create tables if they don't exist
        self.initialize_db()

    def initialize_db(self):
        # Ensure the database exists
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS Lab3_NAH")
        self.conn.database = "Lab3_NAH"

        # Create a table for portfolios if it doesn't already exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                creation_date DATE,
                tickers TEXT
            )
        """)

        # Drop the table containing stock info if it exists
        self.cursor.execute("DROP TABLE IF EXISTS stock_raw_data")

        # Create a table for raw stock data if it doesn't already exist
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stock_raw_data (
            Date datetime,
            Open float,
            High float,
            Low float,
            Close float,
            Adj_Close float,
            Volume float,
            Ticker varchar(20)
        )
        """
        self.cursor.execute(create_table_query)
        # Committing any changes made during the initialization
        self.conn.commit()

    def portfolio_exists(self, tickers):
        # Check if the given portfolio already exists in the database
        tickers_string = ",".join(sorted(tickers))
        self.cursor.execute("SELECT COUNT(*) FROM portfolios WHERE tickers = %s", (tickers_string,))
        count = self.cursor.fetchone()[0]
        return count > 0

    def save_portfolio(self, portfolio):
        # Save portfolio to the database if it doesn't already exist
        tickers = portfolio.get_selected_tickers()
        if self.portfolio_exists(tickers):
            print("\n> This portfolio already exists in the database!")
            return
        tickers_string = ",".join(sorted(tickers))
        self.cursor.execute("INSERT INTO portfolios (creation_date, tickers) VALUES (%s, %s)", 
                            (portfolio.creation_date, tickers_string))
        # Commit the changes
        self.conn.commit()
        print("\n> Portfolio saved to database!")

    def get_all_portfolios(self):
        # Retrieve all portfolios from the database
        self.cursor.execute("SELECT * FROM portfolios")
        portfolios = self.cursor.fetchall()
        return portfolios

    def save_raw_data(self, raw_data):
        # Save raw stock data to the database
        raw_data = raw_data.replace(np.nan,'NaN')
        for i, row in raw_data.iterrows():
            listt = list(row)
            listt.insert(0,i)
            result = tuple(listt)
            insert = "INSERT INTO stock_raw_data values(%s, %s, %s, %s, %s, %s, %s, %s)"
            self.cursor.execute(insert, tuple(result))
        # Commit the changes
        self.conn.commit()

    def close(self):
        # Close the cursor and database connection
        self.cursor.close()
        self.conn.close()
