'''
db_store.py:
    Implement the interface defined in data_store_interface.py to support data storage to the database. 
    Here we take SQLite as an example, you can modify it to other databases as needed.

'''
import pandas as pd                                          
import pymysql

class DBStore:
    def __init__(self):
        self.conn = pymysql.connect(host='localhost',db='Lab3_NAH',user='root',password='Dsci560@1234')
        self.cur = self.conn.cursor()

    def save(self):
        self.cur.execute("DROP TABLE IF EXISTS stock_data")
        create_table_query = """
        CREATE TABLE IF NOT EXISTS stock_data (
            Date datetime,
            Ticker varchar(20),
            Open float,
            High float,
            Low float,
            Close float,
            Adj_Close float,
            Volume float,
            Daily_Return varchar(30),
            SMA varchar(30),
            EMA varchar(30)
        )
        """
        self.cur.execute(create_table_query)
        import numpy as np
        df = pd.read_csv('processed_output.csv')
        df = df.replace(np.nan, 'NaN')

        print(df)
        for i, row in df.iterrows():
            insert = "INSERT INTO stock_data values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            self.cur.execute(insert, tuple(row))

        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()