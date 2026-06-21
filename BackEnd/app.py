import os
from flask import Flask, jsonify, request, send_from_directory, render_template, redirect, url_for, session, flash
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash

# DB functions
from db import get_history, save_message, delete_messages_by_session
from db import get_db_connection, init_db

# Models
from models.users import get_all_users, get_user_by_id, get_user_by_email, create_user, delete_user
from models.chat_sessions import get_sessions_by_user, get_session_by_id, create_session, delete_session
from models.itineraries import get_itineraries_by_user, get_itinerary_by_id, create_itinerary, update_itinerary_status, delete_itinerary
from models.itinerary_day import get_days_by_itinerary, create_day, delete_days_by_itinerary
from models.activities import get_activities_by_day, create_activity, delete_activities_by_day
from models.preferences import get_preferences_by_user, create_preferences, update_preferences
from models.destinations import get_all_destinations, get_destination_id, search_destinations, create_destination

app = Flask(__name__,
    template_folder='../templates',
    static_folder='../static')
app.secret_key = 'tripzen-secret-key'
CORS(app, origins=["http://127.0.0.1:3000", "http://localhost:3000", "http://127.0.0.1:5500", "http://localhost:5500", "http://localhost:5000"])
with app.app_context():
    init_db()

# ─────────────────────────────────────────
# USERS
# ─────────────────────────────────────────

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
    data      = request.get_json()
    full_name = data.get('full_name')
    email     = data.get('email')
    phone     = data.get('phone')
    password  = data.get('password')

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400

    existing = get_user_by_email(email)
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    hashed = generate_password_hash(password)
    new_id = create_user(full_name, email, phone, hashed)
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

    if not check_password_hash(user['password_hash'], password):
        return jsonify({"error": "Wrong password"}), 401

    # Also set Flask session so the home route works
    session['user_id']  = user['id']
    session['username'] = user['full_name']
    session['email']    = user['email']

    return jsonify({
        "message": "Login successful",
        "user_id": user['id'],
        "full_name": user['full_name'],
        "email": user['email']
    }), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    delete_user(user_id)
    return jsonify({"message": "User deleted"}), 200


# ─────────────────────────────────────────
# CHAT SESSIONS
# ─────────────────────────────────────────

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
    data    = request.get_json()
    user_id = data.get('user_id')
    title   = data.get('title')

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


# ─────────────────────────────────────────
# MESSAGES + AI AGENT
# ─────────────────────────────────────────

@app.route('/messages/<int:session_id>', methods=['GET'])
def messages(session_id):
    return jsonify(get_history(session_id)), 200

@app.route('/messages', methods=['POST'])
def new_message():
    data       = request.get_json()
    session_id = data.get('session_id')
    sender     = data.get('sender')
    message    = data.get('message')
    user_id    = data.get('user_id')

    if not session_id or not sender or not message:
        return jsonify({"error": "session_id, sender and message are required"}), 400

    if sender not in ['user', 'bot']:
        return jsonify({"error": "sender must be 'user' or 'bot'"}), 400

    # Save user message to DB
    new_id = save_message(session_id, sender, message)

    bot_reply = None
    if sender == 'user':
        try:
            from agent import run_agent

            # Fetch current session history only
            history = get_history(session_id)
            history_list = [
                {"sender": m["sender"], "message": m["message"]}
                for m in history[:-1]  # exclude the message just saved
            ]

            # Run agent
            bot_reply = run_agent(message, history_list, session_id, user_id)

            # Save bot reply to DB
            save_message(session_id, 'bot', bot_reply)

        except Exception as e:
            print("AGENT ERROR:", str(e))
            bot_reply = f"Error: {str(e)}"
            save_message(session_id, 'bot', bot_reply)

    return jsonify({
        "message": "Message saved",
        "message_id": new_id,
        "bot_reply": bot_reply
    }), 201

@app.route('/messages/<int:session_id>', methods=['DELETE'])
def remove_messages(session_id):
    delete_messages_by_session(session_id)
    return jsonify({"message": "Messages deleted"}), 200


# ─────────────────────────────────────────
# ITINERARIES
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# ITINERARY DAYS
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# ACTIVITIES
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# PREFERENCES
# ─────────────────────────────────────────

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


# ─────────────────────────────────────────
# DESTINATIONS
# ─────────────────────────────────────────

@app.route('/destinations', methods=['GET'])
def destinations():
    return jsonify(get_all_destinations()), 200

@app.route('/destinations/<int:destination_id>', methods=['GET'])
def destination(destination_id):
    dest = get_destination_id(destination_id)
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

@app.route('/static/pdfs/<filename>')
def serve_pdf(filename):
    return send_from_directory(
        os.path.join(os.getcwd(), 'static', 'pdfs'),
        filename
    )


# ─────────────────────────────────────────
# AUTH PAGES (Login / Register UI)
# ─────────────────────────────────────────

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('index.html',
        username=session['username'],
        email=session['email'],
        user_id=session['user_id']
    )

@app.route('/login-page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        user     = get_user_by_email(email)
        if not user or not check_password_hash(user['password_hash'], password):
            flash('Invalid email or password.', 'error')
            return render_template('login.html')
        session['user_id']  = user['id']
        session['username'] = user['full_name']
        session['email']    = user['email']
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/register-page', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        full_name = request.form['username']
        email     = request.form['email']
        password  = request.form['password']
        existing  = get_user_by_email(email)
        if existing:
            flash('Email already registered.', 'error')
            return render_template('register.html')
        hashed = generate_password_hash(password)
        create_user(full_name, email, None, hashed)
        flash('Account created! Please sign in.', 'success')
        return redirect(url_for('login_page'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))


# ─────────────────────────────────────────
# RUN
# ─────────────────────────────────────────

if __name__ == "__main__":
    print("Connecting to database...")
    print("AI Agent ready!")
    app.run(debug=True)