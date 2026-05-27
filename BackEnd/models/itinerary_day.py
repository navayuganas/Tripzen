from app import db

class ItineraryDay(db.Model):
    __tablename__ = "itinerary_days"

    id = db.Column(db.BigInteger, primary_key=True)
    itinerary_id = db.Column(db.BigInteger)
    day_number = db.Column(db.Integer)
    title = db.Column(db.String(255))