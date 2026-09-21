from db import get_db_connection

def get_all_users():
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    cursor.close()
    con.close()
    return users

def get_user_by_id(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    con.close()
    return user

def get_user_by_email(email):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    con.close()
    return user

def create_user(full_name, email,password_hash):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        "INSERT INTO users (full_name, email,password_hash) VALUES (%s, %s, %s)",
        (full_name, email,password_hash)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def delete_user(user_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    con.commit()
    cursor.close()
    con.close()