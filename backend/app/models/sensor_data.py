from app import db
from datetime import datetime

class SensorData(db.Model):
    __tablename__ = "sensor_data"

    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, db.ForeignKey("sensors.id"), nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    sensor = db.relationship("Sensor", backref=db.backref("data", lazy=True))

    def __repr__(self):
        return f"<SensorData sensor={self.sensor_id} value={self.value}>"
