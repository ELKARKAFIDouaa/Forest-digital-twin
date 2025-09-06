from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.role_service import RoleService
from app.utils.role_decorators import can_manage_users
from app.models.user import User
from app import db

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.before_request
@jwt_required(optional=True)
def require_admin():
    if request.method == "OPTIONS":
        return None

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user or not user.has_role("admin"):
        return jsonify({"error": "Forbidden"}), 403


# ------------------ Gestion des rôles ------------------

@admin_bp.route('/roles', methods=['GET'])
def get_roles():
    """Retourne la liste des rôles"""
    roles = RoleService.get_all_roles()
    roles_data = [{'name': role.name, 'description': role.description} for role in roles]
    return jsonify(roles_data)


# ------------------ Gestion des utilisateurs ------------------

@admin_bp.route('/users', methods=['GET'])
@can_manage_users
def get_users():
    """Retourne la liste des utilisateurs avec leurs rôles"""
    users = User.query.all()
    users_data = [
        {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'email': user.email,
            'telephone': user.telephone,
            'roles': [role.name for role in user.roles]  # Correction ici
        }
        for user in users
    ]
    return jsonify(users_data)


@admin_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    # Récupérer l’utilisateur depuis  DB
    from app.models import User
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "firstname": user.firstname,
        "lastname": user.lastname,
    }), 200
@admin_bp.route('/users', methods=['POST'])
def api_create_user():
    """Créer un nouvel utilisateur"""
    data = request.json or {}
    email = data.get("email")
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    telephone = data.get("telephone")
    password = data.get("password")
    role = data.get("role", "agent")

    from app.services.auth_service import AuthService
    user, error = AuthService.register(email, firstname, lastname, telephone, password, role)
    if error:
        return jsonify({"success": False, "message": error}), 400

    return jsonify({
        "success": True,
        "message": "User created",
        "id": user.id,
        "roles": [r.name for r in user.roles]
    }), 201

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def api_delete_user(user_id):
    """Supprimer un utilisateur"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"success": True, "message": "User deleted"})


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def api_update_user(user_id):
    """Modifier un utilisateur"""
    user = User.query.get_or_404(user_id)
    data = request.json or {}
    user.firstname = data.get("firstname", user.firstname)
    user.lastname = data.get("lastname", user.lastname)
    user.email = data.get("email", user.email)
    user.telephone = data.get("telephone", user.telephone)

    if data.get("password"):
        user.set_password(data["password"])

    if "role" in data:
        # Supprimer les anciens rôles et assigner le nouveau
        RoleService.remove_all_roles_from_user(user.id)
        RoleService.assign_role_to_user(user.id, data["role"])

    db.session.commit()
    return jsonify({"success": True, "message": "User updated"})


# ------------------ Assignation de rôle ------------------

@admin_bp.route('/assign-role', methods=['POST'])
def api_assign_role():
    """API pour assigner un rôle"""
    data = request.json or {}
    user_id = data.get('user_id')
    role_name = data.get('role_name')

    if RoleService.assign_role_to_user(user_id, role_name):
        return jsonify({'success': True, 'message': 'Role assigned successfully'})
    return jsonify({'success': False, 'message': 'Error assigning role'}), 400


@admin_bp.route('/remove-role', methods=['POST'])
def api_remove_role():
    """API pour retirer un rôle"""
    data = request.json or {}
    user_id = data.get('user_id')
    role_name = data.get('role_name')

    if RoleService.remove_role_from_user(user_id, role_name):
        return jsonify({'success': True, 'message': 'Role removed successfully'})
    return jsonify({'success': False, 'message': 'Error removing role'}), 400
