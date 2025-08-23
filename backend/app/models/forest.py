from app import db

class Forest(db.Model):
    __tablename__ = 'forests'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    location = db.Column(db.String)  
    surface = db.Column(db.Float)
    
    zones = db.relationship('Zone', backref='forest')