from app import db

class Itinerary(db.Model):
    __tablename__ = "itineraries"

    id = db.Column(db.BigInteger, primary_key=True)
    session_id = db.Column(db.BigInteger)
    destination_id = db.Column(db.BigInteger)
    title = db.Column(db.String(255))
    budget = db.Column(db.Float)
    total_days = db.Column(db.Integer)