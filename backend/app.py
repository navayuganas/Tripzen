from flask import Flask, jsonify, request
from db import get_db_connection

app = Flask(__name__)

@app.route('/getTable', methods=['GET'])
def get_tables():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        con.close()
        table_names = [table[0] for table in tables]
        return jsonify({"tables": table_names}), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Connecting to database...")
    app.run(debug=True)