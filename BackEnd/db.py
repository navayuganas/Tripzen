import mysql.connector

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Yugan-22!!',
    'database': 'chatbot'
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
    # Oldest first
    return [{"sender": r[0], "message": r[1]} for r in reversed(rows)]