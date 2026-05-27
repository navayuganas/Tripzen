from app import db

class Destination(db.Model):
    __tablename__ = "destinations"

    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(100))
    country = db.Column(db.String(100))
    state = db.Column(db.String(100))
    best_time_to_visit = db.Column(db.String(100))