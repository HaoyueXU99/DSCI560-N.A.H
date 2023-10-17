from flask import Flask, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)  

HOSTNAME = "localhost"
DATABASE = "Lab3_NAH"
USERNAME = "Dsci560"
PASSWORD = "Dsci560@1234"
TABLE_NAME = "well_data"

@app.route("/get_well_data", methods=["GET"])
def get_well_data():
    connection = mysql.connector.connect(
        host=HOSTNAME,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    data = cursor.fetchall()

    cursor.close()
    connection.close()

    return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True)
