from app import db
from app.models.roles import Role
from app.models.user import User

class RoleService:
    @staticmethod
    def create_role(name, description=None, permissions=None):
        """Créer un nouveau rôle"""
        if permissions is None:
            permissions = []
            
        role = Role.query.filter_by(name=name).first()
        if role:
            return None  # Le rôle existe déjà
            
        role = Role(name=name, description=description, permissions=permissions)
        db.session.add(role)
        db.session.commit()
        return role
    
    @staticmethod
    def get_all_roles():
        """Récupérer tous les rôles"""
        return Role.query.all()
    
    @staticmethod
    def get_role_by_name(role_name):
        """Récupérer un rôle par son nom"""
        return Role.query.filter_by(name=role_name).first()
    
    @staticmethod
    def assign_role_to_user(user_id, role_name):
        """Assigner un rôle à un utilisateur"""
        user = User.query.get(user_id)
        role = Role.query.filter_by(name=role_name).first()
        
        if user and role:
            user.add_role(role)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def remove_role_from_user(user_id, role_name):
        """Retirer un rôle d'un utilisateur"""
        user = User.query.get(user_id)
        if user:
            user.remove_role(role_name)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_user_roles(user_id):
        """Récupérer les rôles d'un utilisateur"""
        user = User.query.get(user_id)
        return user.roles if user else []
    
    @staticmethod
    def initialize_default_roles():
        """Initialiser les rôles par défaut"""
        default_roles = [
            {
                'name': 'admin',
                'description': 'Administrateur du système',
                'permissions': ['manage_users', 'manage_roles', 'view_dashboard', 'manage_iot']
            },
            {
                'name': 'forest_agent',
                'description': 'Agent forestier',
                'permissions': ['view_dashboard', 'manage_iot', 'view_reports']
            },
            {
                'name': 'researcher',
                'description': 'Chercheur',
                'permissions': ['view_dashboard', 'view_reports', 'run_predictions']
            },
            {
                'name': 'viewer',
                'description': 'Observateur',
                'permissions': ['view_dashboard']
            }
        ]
        
        for role_data in default_roles:
            if not Role.query.filter_by(name=role_data['name']).first():
                RoleService.create_role(
                    role_data['name'],
                    role_data['description'],
                    role_data['permissions']
                )