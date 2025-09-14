from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.auth_service import AuthService
from app.models.user import User


auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    email = data.get("email")
    telephone = data.get("telephone")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user, error = AuthService.register(email, firstname, lastname, telephone, password, role="user")
    if error:
        return jsonify({"error": error}), 400

    # ✅ Créer un token JWT pour le nouvel utilisateur
    access_token = create_access_token(identity=str(user.id))

    
    return jsonify({
        "message": "Utilisateur créé avec succès",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "telephone": user.telephone,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    }), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = AuthService.login(email, password)
    if not user:
        return jsonify({"error": "Identifiants invalides"}), 401

    # ✅ Créer un token JWT
    access_token = create_access_token(identity=str(user.id))

    
    return jsonify({
        "message": "Connexion réussie",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "telephone": user.telephone,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    })

@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Utilisateur non trouvé"}), 404

    return jsonify({
        "id": user.id,
        "email": user.email,
        "firstname": user.firstname,
        "lastname": user.lastname,
        "telephone": user.telephone,
        "role": user.role,
        "created_at": user.created_at.isoformat() if user.created_at else None
    })