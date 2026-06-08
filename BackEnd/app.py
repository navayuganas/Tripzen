from flask import Flask, jsonify, request
from flask_cors import CORS
from db import get_db_connection


from models.users import get_all_users, get_user_by_id, get_user_by_email, create_user, delete_user
from models.chat_sessions import get_sessions_by_user, get_session_by_id, create_session, delete_session
from models.messages import get_messages_by_session, create_message, delete_messages_by_session
from models.itineraries import get_itineraries_by_user, get_itinerary_by_id, create_itinerary, update_itinerary_status, delete_itinerary
from models.itinerary_day import get_days_by_itinerary, create_day, delete_days_by_itinerary
from models.activities import get_activities_by_day, create_activity, delete_activities_by_day
from models.preferences import get_preferences_by_user, create_preferences, update_preferences
from models.destinations import get_all_destinations, get_destination_id, search_destinations, create_destination
from agent import run_agent

app = Flask(__name__)
CORS(app)

@app.route('/getTable', methods=['GET'])
def get_tables():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        cursor.close()
        con.close()
        table_names = [table[0] for table in tables]
        return jsonify({"tables": table_names}), 200
    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/users', methods=['GET'])
def users():
    return jsonify(get_all_users()), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    full_name = data.get('full_name')
    email     = data.get('email')
    phone     = data.get('phone')
    password  = data.get('password')

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    new_id = create_user(full_name, email, phone, password)
    return jsonify({"message": "User registered", "user_id": new_id}), 201

@app.route('/login', methods=['POST'])
def login():
    data     = request.get_json()
    email    = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = get_user_by_email(email)
    if not user:
        return jsonify({"error": "User not found"}), 404

    if user['password_hash'] != password:
        return jsonify({"error": "Wrong password"}), 401

    return jsonify({"message": "Login successful", "user_id": user['id']}), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    delete_user(user_id)
    return jsonify({"message": "User deleted"}), 200

@app.route('/sessions/<int:user_id>', methods=['GET'])
def sessions(user_id):
    return jsonify(get_sessions_by_user(user_id)), 200

@app.route('/sessions/<int:session_id>/details', methods=['GET'])
def session_details(session_id):
    session = get_session_by_id(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session), 200

@app.route('/sessions', methods=['POST'])
def new_session():
    data     = request.get_json()
    user_id  = data.get('user_id')
    title    = data.get('title')

    if not user_id or not title:
        return jsonify({"error": "user_id and title are required"}), 400

    new_id = create_session(user_id, title)
    return jsonify({"message": "Session created", "session_id": new_id}), 201

@app.route('/sessions/<int:session_id>', methods=['DELETE'])
def remove_session(session_id):
    session = get_session_by_id(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    delete_session(session_id)
    return jsonify({"message": "Session deleted"}), 200

@app.route('/messages/<int:session_id>', methods=['GET'])
def messages(session_id):
    return jsonify(get_messages_by_session(session_id)), 200

@app.route('/messages', methods=['POST'])
def new_message():
    data       = request.get_json()
    session_id = data.get('session_id')
    sender     = data.get('sender')
    message    = data.get('message')

    if not session_id or not sender or not message:
        return jsonify({"error": "session_id, sender and message are required"}), 400

    if sender not in ['user', 'bot']:
        return jsonify({"error": "sender must be 'user' or 'bot'"}), 400

    new_id = create_message(session_id, sender, message)
    return jsonify({"message": "Message saved", "message_id": new_id}), 201

@app.route('/messages/<int:session_id>', methods=['DELETE'])
def remove_messages(session_id):
    delete_messages_by_session(session_id)
    return jsonify({"message": "Messages deleted"}), 200

@app.route('/itineraries/<int:user_id>', methods=['GET'])
def itineraries(user_id):
    return jsonify(get_itineraries_by_user(user_id)), 200

@app.route('/itineraries/<int:itinerary_id>/details', methods=['GET'])
def itinerary_details(itinerary_id):
    itinerary = get_itinerary_by_id(itinerary_id)
    if not itinerary:
        return jsonify({"error": "Itinerary not found"}), 404
    return jsonify(itinerary), 200

@app.route('/itineraries', methods=['POST'])
def new_itinerary():
    data = request.get_json()
    new_id = create_itinerary(
        data.get('session_id'),
        data.get('user_id'),
        data.get('title'),
        data.get('destination'),
        data.get('start_date'),
        data.get('end_date'),
        data.get('total_days'),
        data.get('budget'),
        data.get('travelers_count'),
        data.get('trip_type'),
        data.get('ai_summary')
    )
    return jsonify({"message": "Itinerary created", "itinerary_id": new_id}), 201

@app.route('/itineraries/<int:itinerary_id>/status', methods=['PUT'])
def update_status(itinerary_id):
    data   = request.get_json()
    status = data.get('status')
    if status not in ['draft', 'customized', 'approved', 'booked']:
        return jsonify({"error": "Invalid status"}), 400
    update_itinerary_status(itinerary_id, status)
    return jsonify({"message": "Status updated"}), 200

@app.route('/itineraries/<int:itinerary_id>', methods=['DELETE'])
def remove_itinerary(itinerary_id):
    delete_itinerary(itinerary_id)
    return jsonify({"message": "Itinerary deleted"}), 200

@app.route('/itinerary/<int:itinerary_id>/days', methods=['GET'])
def itinerary_days(itinerary_id):
    return jsonify(get_days_by_itinerary(itinerary_id)), 200

@app.route('/itinerary/days', methods=['POST'])
def new_day():
    data = request.get_json()
    new_id = create_day(
        data.get('itinerary_id'),
        data.get('day_number'),
        data.get('title'),
        data.get('description'),
        data.get('hotel_name'),
        data.get('transport_mode'),
        data.get('estimated_cost')
    )
    return jsonify({"message": "Day created", "day_id": new_id}), 201

@app.route('/itinerary/<int:itinerary_id>/days', methods=['DELETE'])
def remove_days(itinerary_id):
    delete_days_by_itinerary(itinerary_id)
    return jsonify({"message": "Days deleted"}), 200

@app.route('/activities/<int:itinerary_day_id>', methods=['GET'])
def activities(itinerary_day_id):
    return jsonify(get_activities_by_day(itinerary_day_id)), 200

@app.route('/activities', methods=['POST'])
def new_activity():
    data = request.get_json()
    new_id = create_activity(
        data.get('itinerary_day_id'),
        data.get('activity_name'),
        data.get('location'),
        data.get('activity_time'),
        data.get('cost'),
        data.get('notes')
    )
    return jsonify({"message": "Activity created", "activity_id": new_id}), 201

@app.route('/activities/<int:itinerary_day_id>', methods=['DELETE'])
def remove_activities(itinerary_day_id):
    delete_activities_by_day(itinerary_day_id)
    return jsonify({"message": "Activities deleted"}), 200

@app.route('/preferences/<int:user_id>', methods=['GET'])
def preferences(user_id):
    prefs = get_preferences_by_user(user_id)
    if not prefs:
        return jsonify({"error": "Preferences not found"}), 404
    return jsonify(prefs), 200

@app.route('/preferences', methods=['POST'])
def new_preferences():
    data = request.get_json()
    new_id = create_preferences(
        data.get('user_id'),
        data.get('preferred_budget_type'),
        data.get('preferred_transport'),
        data.get('preferred_hotel_rating'),
        data.get('favorite_destinations'),
        data.get('food_preferences')
    )
    return jsonify({"message": "Preferences saved", "preference_id": new_id}), 201

@app.route('/preferences/<int:user_id>', methods=['PUT'])
def edit_preferences(user_id):
    data = request.get_json()
    update_preferences(
        user_id,
        data.get('preferred_budget_type'),
        data.get('preferred_transport'),
        data.get('preferred_hotel_rating'),
        data.get('favorite_destinations'),
        data.get('food_preferences')
    )
    return jsonify({"message": "Preferences updated"}), 200

@app.route('/destinations', methods=['GET'])
def destinations():
    return jsonify(get_all_destinations()), 200

@app.route('/destinations/<int:destination_id>', methods=['GET'])
def destination(destination_id):
    dest = get_destination_by_id(destination_id)
    if not dest:
        return jsonify({"error": "Destination not found"}), 404
    return jsonify(dest), 200

@app.route('/destinations/search', methods=['GET'])
def destination_search():
    city    = request.args.get('city', '')
    country = request.args.get('country', '')
    return jsonify(search_destinations(city, country)), 200

@app.route('/destinations', methods=['POST'])
def new_destination():
    data = request.get_json()
    new_id = create_destination(
        data.get('country'),
        data.get('city'),
        data.get('description'),
        data.get('avg_budget_per_day'),
        data.get('best_season')
    )
    return jsonify({"message": "Destination created", "destination_id": new_id}), 201

@app.route('/chat', methods=['POST'])
def chat():
    data       = request.get_json()
    session_id = data.get('session_id')
    user_id    = data.get('user_id')
    message    = data.get('message')

    if not session_id or not message:
        return jsonify({"error": "session_id and message are required"}), 400

    try:
        create_message(session_id, 'user', message)
        history   = get_messages_by_session(session_id)
        bot_reply = run_agent(message, history)
        create_message(session_id, 'bot', bot_reply)
        return jsonify({
            "user_message": message,
            "bot_reply"   : bot_reply
        }), 200

    except Exception as e:
        print("❌ CHAT ERROR:", str(e))          # ← shows in terminal
        import traceback
        traceback.print_exc()                    # ← shows full error
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Connecting to database...")
    app.run(debug=True)