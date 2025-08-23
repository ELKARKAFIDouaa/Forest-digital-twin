from flask import Blueprint, request, jsonify, session
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__)

# 🔹 Inscription
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.get_json()
    email = data.get("email")
    telephone = data.get("telephone")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email et mot de passe requis"}), 400

    user, error = AuthService.register(email, telephone, password, role="user")
    if error:
        return jsonify({"error": error}), 400

    return jsonify({"message": "Utilisateur créé avec succès", "id": user.id}), 201


# 🔹 Connexion
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = AuthService.login(email, password)
    if not user:
        return jsonify({"error": "Identifiants invalides"}), 401

    
    session["user_id"] = user.id
    return jsonify({"message": "Connexion réussie", "user_id": user.id, "role": user.role})

