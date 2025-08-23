from app import db
from app.models.associations import user_roles


class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)  
    
    
    users = db.relationship('User', secondary=user_roles, back_populates="roles")
    
    def __repr__(self):
        return f'<Role {self.name}>'


