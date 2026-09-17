import os
import mysql.connector

DB_CONFIG = {
    'host': os.getenv('MYSQLHOST', 'localhost'),
    'user': os.getenv('MYSQLUSER', 'root'),
    'password': os.getenv('MYSQLPASSWORD', 'Yugan-22!!'),
    'database': os.getenv('MYSQLDATABASE', 'chatbot'),
    'port': int(os.getenv('MYSQLPORT', 3306))
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# ── Save one message ──
def save_message(session_id, sender, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (session_id, sender, message)
        VALUES (%s, %s, %s)
    """, (session_id, sender, message))
    conn.commit()
    cursor.close()
    conn.close()

# ── Get history by session only ──
def get_history(session_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, message FROM messages
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (session_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"sender": r[0], "message": r[1]} for r in reversed(rows)]

# ── Delete all messages in a session ──
def delete_messages_by_session(session_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ── LONG TERM MEMORY — Get ALL past messages by user_id ──
def get_user_history(user_id, limit=30):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.sender, m.message
        FROM messages m
        JOIN chat_sessions cs ON m.session_id = cs.id
        WHERE cs.user_id = %s
        ORDER BY m.created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"sender": r[0], "message": r[1]} for r in reversed(rows)]

# ── Create all tables if they don't exist ──
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            email VARCHAR(150) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Chat Sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) DEFAULT 'New Trip',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # 3. Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id INT NOT NULL,
            sender VARCHAR(50) NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()