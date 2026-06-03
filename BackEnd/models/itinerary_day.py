from db import get_db_connection

def get_days_by_itinerary(itinerary_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM itinerary_days WHERE itinerary_id = %s ORDER BY day_number ASC",
        (itinerary_id,)
    )
    days = cursor.fetchall()
    cursor.close()
    con.close()
    return days

def create_day(itinerary_id, day_number, title, description,
               hotel_name, transport_mode, estimated_cost):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """INSERT INTO itinerary_days
        (itinerary_id, day_number, title, description, hotel_name, transport_mode, estimated_cost)
        VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (itinerary_id, day_number, title, description,
         hotel_name, transport_mode, estimated_cost)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def delete_days_by_itinerary(itinerary_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM itinerary_days WHERE itinerary_id = %s", (itinerary_id,))
    con.commit()
    cursor.close()
    con.close()