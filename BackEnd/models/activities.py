from db import get_db_connection

def get_activities_by_day(itinerary_day_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM activities WHERE itinerary_day_id = %s ORDER BY activity_time ASC",
        (itinerary_day_id,)
    )
    activities = cursor.fetchall()
    cursor.close()
    con.close()
    return activities

def create_activity(itinerary_day_id, activity_name, location,
                    activity_time, cost, notes):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """INSERT INTO activities
        (itinerary_day_id, activity_name, location, activity_time, cost, notes)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (itinerary_day_id, activity_name, location, activity_time, cost, notes)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def delete_activities_by_day(itinerary_day_id):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute("DELETE FROM activities WHERE itinerary_day_id = %s", (itinerary_day_id,))
    con.commit()
    cursor.close()
    con.close()