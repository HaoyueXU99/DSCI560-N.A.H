import pandas as pd
import mysql.connector


HOSTNAME = "localhost"
DATABASE = "Lab3_NAH"
USERNAME = "Dsci560"
PASSWORD = "Dsci560@1234"
TABLE_NAME = "well_data"

def csv_to_mysql():

    df = pd.read_csv('data.csv')

    df.columns = [col.replace(" ", "_").replace("#", "Number").replace("Acid%", "Acid_Percentage") for col in df.columns]

    connection = mysql.connector.connect(
        host=HOSTNAME,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = connection.cursor()

    columns = ", ".join([f"`{col}` TEXT" if col == "Details" else f"`{col}` VARCHAR(255)" for col in df.columns])
    create_table_query = f"CREATE TABLE IF NOT EXISTS {TABLE_NAME} ({columns})"
    cursor.execute(create_table_query)


    for index, row in df.iterrows():
        values = tuple(row)
        insert_query = f"INSERT INTO {TABLE_NAME} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(row))})"
        cursor.execute(insert_query, values)

    connection.commit()
    cursor.close()
    connection.close()
    print("Data has been imported to MySQL successfully!")

if __name__ == "__main__":
    csv_to_mysql()
