from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.services.role_service import RoleService
from app.services.auth_service import AuthService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

# ----------------------------
# MIDDLEWARE: Vérifier admin
# ----------------------------
@admin_bp.before_request
@jwt_required(optional=True)
def require_admin():
    if request.method == "OPTIONS":
        return None  # laisser passer les pré-requêtes CORS

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user or not user.has_role("admin"):
        return jsonify({"error": "Forbidden"}), 403


# ----------------------------
# RÔLES
# ----------------------------
@admin_bp.route("/roles", methods=["GET"])
def list_roles():
    """Retourne la liste des rôles disponibles"""
    roles = RoleService.get_all_roles()
    return jsonify([{
        "name": role.name,
        "description": role.description,
        "permissions": role.permissions
    } for role in roles])


@admin_bp.route("/assign-role", methods=["POST"])
def assign_role():
    """Assigner un rôle à un utilisateur"""
    data = request.json or {}
    if RoleService.assign_role_to_user(data.get("user_id"), data.get("role_name")):
        return jsonify({"message": "Role assigned successfully"})
    return jsonify({"error": "Error assigning role"}), 400


@admin_bp.route("/remove-role", methods=["POST"])
def remove_role():
    """Retirer un rôle d’un utilisateur"""
    data = request.json or {}
    if RoleService.remove_role_from_user(data.get("user_id"), data.get("role_name")):
        return jsonify({"message": "Role removed successfully"})
    return jsonify({"error": "Error removing role"}), 400

@admin_bp.route("/delete-role", methods=["POST"])
def delete_role():
    """Supprimer un rôle complètement"""
    data = request.json or {}
    role_name = data.get("role_name")

    if not role_name:
        return jsonify({"error": "Role name required"}), 400

    if RoleService.delete_role(role_name):
        return jsonify({"message": f"Role '{role_name}' deleted successfully"})
    return jsonify({"error": "Error deleting role"}), 400

@admin_bp.route("/update-role", methods=["POST"])
def update_role():
    """Mettre à jour un rôle existant"""
    data = request.json or {}
    role_name = data.get("role_name")
    updated_data = {
        "name": data.get("name"),
        "description": data.get("description"),
        "permissions": data.get("permissions")
    }

    if not role_name:
        return jsonify({"error": "Role name required"}), 400

    if RoleService.update_role(role_name, updated_data):
        return jsonify({"message": f"Role '{role_name}' updated successfully"})
    return jsonify({"error": "Error updating role"}), 400

# ----------------------------
# UTILISATEURS CRUD
# ----------------------------
@admin_bp.route("/users", methods=["GET"])
def list_users():
    """Retourne la liste de tous les utilisateurs"""
    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "firstname": u.firstname,
        "lastname": u.lastname,
        "email": u.email,
        "telephone": u.telephone,
        "roles": [r.name for r in u.roles]
    } for u in users])


@admin_bp.route("/users/add", methods=["POST"])
def create_user():
    data = request.json or {}
    user, error = AuthService.register(
        data.get("email"),
        data.get("firstname"),
        data.get("lastname"),
        data.get("telephone"),
        data.get("password"),
        data.get("role", "agent"),
    )
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "User created",
        "id": user.id,
        "roles": [r.name for r in user.roles]
    }), 201


@admin_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    """Retourne les infos d’un utilisateur"""
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "email": user.email,
        "telephone": user.telephone,
        "roles": [r.name for r in user.roles]
    })


@admin_bp.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
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
    # supprimer tous les rôles existants
     for r in user.roles:
        RoleService.remove_role_from_user(user.id, r.name)
    # assigner le nouveau
    RoleService.assign_role_to_user(user.id, data["role"])


    db.session.commit()
    return jsonify({"message": "User updated"})


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Supprimer un utilisateur"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"})


# ----------------------------
# ADMIN INFO
# ----------------------------
@admin_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    """Retourne les infos de l’admin connecté + nouveau token"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "Utilisateur introuvable"}), 404

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "id": user.id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "telephone": user.telephone,
        "roles": [r.name for r in user.roles],
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "access_token": token
    })
