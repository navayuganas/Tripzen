# models/chat_sessions.py
from db import get_db_connection

def get_sessions_by_user(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chat_sessions WHERE user_id = %s", (user_id,))
    sessions = cursor.fetchall()
    cursor.close()
    con.close()
    return sessions

def get_session_by_id(session_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM chat_sessions WHERE id = %s", (session_id,))
    session = cursor.fetchone()
    cursor.close()
    con.close()
    return session

def create_session(user_id, title):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO chat_sessions (user_id, title) VALUES (%s, %s)",
        (user_id, title)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def delete_session(session_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM chat_sessions WHERE id = %s", (session_id,))
    con.commit()
    cursor.close()
    con.close()