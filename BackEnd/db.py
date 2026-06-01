import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '#October1again',
    'database': 'chatbot'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)