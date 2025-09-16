# app/models/alert.py
from app import db
from datetime import datetime

class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    acknowledged = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "severity": self.severity,
            "sensor_id": self.sensor_id,
            "created_at": self.created_at.isoformat(),
            "acknowledged": self.acknowledged,
        }

    def __repr__(self):
        return f"<Alert {self.message} for Sensor {self.sensor_id}>"
