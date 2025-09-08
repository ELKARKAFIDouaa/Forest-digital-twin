from app import db

class Sensor(db.Model):
    __tablename__ = "sensors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    # Optionnel : min/max pour générer des valeurs réalistes
    min_value = db.Column(db.Float, nullable=True)
    max_value = db.Column(db.Float, nullable=True)


    def __repr__(self):
        return f"<Sensor {self.name} ({self.type})>"
