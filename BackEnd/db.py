import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Yugan-22!!',
    'database': 'chatbot'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)