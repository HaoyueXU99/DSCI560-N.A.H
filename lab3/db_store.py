'''
db_store.py:
    Implement the interface defined in data_store_interface.py to support data storage to the database. 
    Here we take SQLite as an example, you can modify it to other databases as needed.

'''

import sqlite3
from data_store_interface import DataStoreInterface

class DBStore(DataStoreInterface):
    def __init__(self, db_path="output.db"):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def save(self, data):
        for ticker, df in data.items():
            df.to_sql(ticker, self.conn, if_exists='replace')
        self.conn.commit()

    def close(self):
        self.conn.close()
