from app import db
from datetime import datetime

class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "Air Temperature"
    category = db.Column(db.String(50), nullable=False)  # Air, Soil, Plant, etc.
    type = db.Column(db.String(100), nullable=False)  # e.g. "Temperature", "Humidity"
    unit = db.Column(db.String(20))  # e.g. "°C", "%", "lux"
    interface = db.Column(db.String(50))  # e.g. I2C, UART, GPIO
    reference = db.Column(db.String(100))  # e.g. "Bosch BME280"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Sensor {self.name}>"
