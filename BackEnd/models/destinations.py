from db import get_db_connection

def get_all_destinations():
    con=get_db_connection()
    cursor=con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM destinations")
    destinations=cursor.fetchall()
    cursor.close()
    con.close()
    return destinations

def get_destination_id(destination_id):
    con=get_db_connection()
    cursor=con.cursor(dictionary=True)
    cursor.execute("SELECT * FROM destinations WHERER id = %s",(destination_id))
    destination=cursor.fetchone()
    cursor.close()
    con.close()
    return destination

def search_destinations(city=None,country=None):
    con=get_db_connection()
    cursor=con.cursor(dictionary=True)
    cursor.execute("SELECT * destinations WHERE city LIKE %s OR country LIKE %s",(f"%{city}%"),f"%country%")
    destinations=cursor.fetchall()
    cursor.close()
    con.close()
    return destinations

def create_destination(city,country,description,avg_budget_per_day,best_season):
    con=get_db_connection()
    cursor=con.cursor(dictionary=True)
    cursor.execute("""INSERT INTO destinations(city,country,description,avg_budget_per_day,best_season)VALUES(%s , %s, %s, %s)""",
                   (city,country,description,avg_budget_per_day,best_season))
    con.commit()
    new_id=cursor.lastrowid
    cursor.close()
    con.close()
    return new_id