from app import db
from datetime import datetime

class SensorData(db.Model):
    __tablename__ = "sensor_data"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id", ondelete="CASCADE"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Correct relationship without backref
    sensor = db.relationship("Sensor", lazy="joined")

    def __repr__(self):
        return f"<SensorData sensor_id={self.sensor_id} value={self.value} at {self.timestamp}>"
