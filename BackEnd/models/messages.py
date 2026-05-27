from app import db

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger)
    message = db.Column(db.Text)
    sender = db.Column(db.String(50))
    created_at = db.Column(db.DateTime)