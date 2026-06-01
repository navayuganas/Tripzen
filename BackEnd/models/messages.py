# models/messages.py
from db import get_db_connection

def get_messages_by_session(session_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM messages WHERE session_id = %s ORDER BY created_at ASC", (session_id,))
    messages = cursor.fetchall()
    cursor.close()
    con.close()
    return messages

def create_message(session_id, sender, message):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, sender, message) VALUES (%s, %s, %s)",
        (session_id, sender, message)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def delete_messages_by_session(session_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM messages WHERE session_id = %s", (session_id,))
    con.commit()
    cursor.close()
    con.close()