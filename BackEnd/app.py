from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

@app.route("/")
def home():
    return "Backend working"

if __name__ == "__main__":
    app.run(debug=True)

    from flask import request, jsonify
from models.message import Message
from app import db

@app.route("/send", methods=["POST"])
def send_message():
    data = request.json

    msg = Message(
        session_id=data["session_id"],
        message=data["message"],
        sender="user"
    )

    db.session.add(msg)
    db.session.commit()

    return jsonify({"status": "message saved"})