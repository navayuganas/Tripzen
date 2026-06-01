# models/itineraries.py
from db import get_db_connection

def get_itineraries_by_user(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM itineraries WHERE user_id = %s", (user_id,))
    itineraries = cursor.fetchall()
    cursor.close()
    con.close()
    return itineraries

def get_itinerary_by_id(itinerary_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM itineraries WHERE id = %s", (itinerary_id,))
    itinerary = cursor.fetchone()
    cursor.close()
    con.close()
    return itinerary

def create_itinerary(session_id, user_id, title, destination, start_date, end_date,
                     total_days, budget, travelers_count, trip_type, ai_summary):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """INSERT INTO itineraries 
        (session_id, user_id, title, destination, start_date, end_date,
         total_days, budget, travelers_count, trip_type, ai_summary)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
        (session_id, user_id, title, destination, start_date, end_date,
         total_days, budget, travelers_count, trip_type, ai_summary)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def update_itinerary_status(itinerary_id, status):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        "UPDATE itineraries SET status = %s WHERE id = %s",
        (status, itinerary_id)
    )
    con.commit()
    cursor.close()
    con.close()

def delete_itinerary(itinerary_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM itineraries WHERE id = %s", (itinerary_id,))
    con.commit()
    cursor.close()
    con.close()