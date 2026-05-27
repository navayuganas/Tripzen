from app import db

class Activity(db.Model):
    __tablename__ = "activities"

    id = db.Column(db.BigInteger, primary_key=True)
    itinerary_day_id = db.Column(db.BigInteger)
    activity_name = db.Column(db.String(255))
    location = db.Column(db.String(255))
    cost = db.Column(db.Float)