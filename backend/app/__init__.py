from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object("config.Config")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)

    # Default login settings
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp)

    from app.routes.sensors import sensors_bp
    app.register_blueprint(sensors_bp, url_prefix="/api")

    # Import models
    from app.models.user import User
    from app.models.roles import Role
    from app.models.associations import user_roles

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    from app.services.role_service import RoleService

    # Create tables and initial users
    with app.app_context():
        db.create_all()  # Ensure all tables exist

        # Add initial users if none exist
        if User.query.count() == 0:
            admin = User(email="admin@forest.com", role="admin", telephone="+123456789")
            admin.set_password("admin123")

            agent = User(email="agent@forest.com", role="agent forestier", telephone="+123456725")
            agent.set_password("agent123")

            chercheur = User(email="chercheur@forest.com", role="chercheur", telephone="+123256789")
            chercheur.set_password("chercheur123")

            db.session.add_all([admin, agent, chercheur])
            db.session.commit()

            
        RoleService.initialize_default_roles()

        @app.route("/")
        def home():
            return "Welcome to Forest Digital Twin API"


    return app
