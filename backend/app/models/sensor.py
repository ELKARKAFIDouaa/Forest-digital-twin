from app import db

class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="active")  
    battery_level = db.Column(db.Integer, nullable=True, default=100)   
    zone = db.Column(db.String(50), nullable=True)                      
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)


    def __repr__(self):
        return f"<Sensor {self.name} ({self.type})>"
def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "type": self.type,
            "unit": self.unit,
            "status": self.status,
            "battery_level": self.battery_level,
            "zone": self.zone,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }