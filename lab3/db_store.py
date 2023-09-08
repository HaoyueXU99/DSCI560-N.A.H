'''
db_store.py:
    Implement the interface defined in data_store_interface.py to support data storage to the database. 
    Here we take SQLite as an example, you can modify it to other databases as needed.

'''

import mysql.connector

class DBStore:
    def __init__(self, host='localhost', user='root', password='', dbname='portfolio_db'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=dbname
        )
        self.cursor = self.conn.cursor(buffered=True)
        self.initialize_db()

    def initialize_db(self):
        # Create database if it doesn't exist
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS portfolio_db")
        self.conn.database = "portfolio_db"

        # Create table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS portfolios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                creation_date DATE,
                tickers TEXT
            )
        """)
        self.conn.commit()

    def save_portfolio(self, portfolio):
        tickers_string = ",".join(portfolio.get_selected_tickers())
        self.cursor.execute("INSERT INTO portfolios (creation_date, tickers) VALUES (%s, %s)", 
                            (portfolio.creation_date, tickers_string))
        self.conn.commit()

    def get_all_portfolios(self):
        self.cursor.execute("SELECT * FROM portfolios")
        portfolios = self.cursor.fetchall()
        return portfolios

    def close(self):
        self.cursor.close()
        self.conn.close()
