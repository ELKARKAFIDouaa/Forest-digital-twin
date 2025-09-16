from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.alert import Alert
from app.models.user import User

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


# Middleware: accès admin + agent
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from flask import jsonify, request
from app.models.user import User

@alerts_bp.before_request
def check_role():
    # Laisser passer le preflight CORS
    if request.method == "OPTIONS":
        return "", 200

    try:
        # Vérifie le JWT dans la requête (header Authorization)
        verify_jwt_in_request()
    except Exception:
        return jsonify({"error": "Unauthorized"}), 401

    user_id = get_jwt_identity()
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)
    if not user or not (user.has_role("admin") or user.has_role("agent")):
        return jsonify({"error": "Forbidden"}), 403

# GET: toutes les alertes
@alerts_bp.route("/", methods=["GET"])
def list_alerts():
    alerts = Alert.query.order_by(Alert.created_at.desc()).all()
    return jsonify([a.to_dict() for a in alerts])


# POST: créer une alerte
@alerts_bp.route("/", methods=["POST"])
def create_alert():
    data = request.json or {}
    alert = Alert(
        message=data.get("message"),
        severity=data.get("severity", "medium"),
        sensor_id=data.get("sensor_id"),
    )
    db.session.add(alert)
    db.session.commit()
    return jsonify(alert.to_dict()), 201


# PATCH: acquitter une alerte
@alerts_bp.route("/<int:alert_id>/ack", methods=["PATCH"])
def acknowledge_alert(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    alert.acknowledged = True
    db.session.commit()
    return jsonify(alert.to_dict())
