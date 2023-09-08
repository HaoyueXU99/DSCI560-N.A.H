import pandas as pd                                          
import pymysql

conn = pymysql.connect(host='localhost',db='Lab3_NAH',user='root',password='Dsci560@1234')
cur = conn.cursor()

cur.execute("DROP TABLE IF EXISTS tesla")
create_table_query = """
CREATE TABLE IF NOT EXISTS tesla (
    Date datetime,
    Open float,
    High float,
    Low float,
    Close float,
    Adj_Close float,
    Volume float,
    Daily_Return float,
    SMA float,
    EMA float
)
"""
cur.execute(create_table_query)

table_name = 'tesla'
df = pd.read_csv('LAb3.csv')
for i, row in df.iterrows():
    insert = "INSERT INTO tesla values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cur.execute(insert, tuple(row))

conn.commit()
cur.close()
conn.close()