from db import get_db_connection

def get_preferences_by_user(user_id):
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM preferences WHERE user_id = %s", (user_id,))
    preferences = cursor.fetchone()
    cursor.close()
    con.close()
    return preferences

def create_preferences(user_id, preferred_budget_type, preferred_transport,
                       preferred_hotel_rating, favorite_destinations, food_preferences):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """INSERT INTO preferences
        (user_id, preferred_budget_type, preferred_transport,
         preferred_hotel_rating, favorite_destinations, food_preferences)
        VALUES (%s, %s, %s, %s, %s, %s)""",
        (user_id, preferred_budget_type, preferred_transport,
         preferred_hotel_rating, favorite_destinations, food_preferences)
    )
    con.commit()
    new_id = cursor.lastrowid
    cursor.close()
    con.close()
    return new_id

def update_preferences(user_id, preferred_budget_type, preferred_transport,
                       preferred_hotel_rating, favorite_destinations, food_preferences):
    con = get_db_connection()
    cursor = con.cursor()
    cursor.execute(
        """UPDATE preferences SET
        preferred_budget_type=%s, preferred_transport=%s,
        preferred_hotel_rating=%s, favorite_destinations=%s, food_preferences=%s
        WHERE user_id=%s""",
        (preferred_budget_type, preferred_transport, preferred_hotel_rating,
         favorite_destinations, food_preferences, user_id)
    )
    con.commit()
    cursor.close()
    con.close()