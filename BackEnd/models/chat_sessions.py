from app import db

class ChatSession(db.Model):
    __tablename__ = "chat_sessions"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger)
    title = db.Column(db.String(255))
    created_at = db.Column(db.DateTime)