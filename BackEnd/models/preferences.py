from app import db

class Preference(db.Model):
    __tablename__ = "preferences"

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger)
    preference_key = db.Column(db.String(100))
    preference_value = db.Column(db.String(255))