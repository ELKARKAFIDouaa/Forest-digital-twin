from app.models.user import User
from app import db

class AuthService:
    @staticmethod
    def register(email, telephone, password, role):

        if User.query.filter_by(email=email).first():
            return None, "Email déjà utilisé"

        user = User(email=email, telephone=telephone, role=role)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def login(email, password):
    
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return user
        return None
