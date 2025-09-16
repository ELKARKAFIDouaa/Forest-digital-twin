from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.sensor import Sensor
from app.models.sensor_data import SensorData
from app.models.alert import Alert
from functools import wraps

sensors_bp = Blueprint("sensors", __name__, url_prefix="/api/sensors")


# ----------------------------
# UTILS: Vérifier rôle autorisé
# ----------------------------
def require_roles(*roles):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            if not user_id:
                return jsonify({"error": "Unauthorized"}), 401

            user = User.query.get(user_id)
            if not user or not any(user.has_role(r) for r in roles):
                return jsonify({"error": "Forbidden"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


# ----------------------------
# SENSOR CRUD
# ----------------------------
@sensors_bp.route("", methods=["GET"])
@sensors_bp.route("/", methods=["GET"])
@jwt_required()
@require_roles("admin", "agent")
def list_sensors():
    sensors = Sensor.query.all()
    result = []
    for s in sensors:
        last_reading = (
            SensorData.query.filter_by(sensor_id=s.id)
            .order_by(SensorData.timestamp.desc())
            .first()
        )
        result.append({
            "id": s.id,
            "name": s.name,
            "category": s.category,
            "type": s.type,
            "unit": s.unit,
            "status": s.status,
            "battery_level": s.battery_level,
            "latitude": s.latitude,
            "longitude": s.longitude,
            "zone": s.zone or "Inconnue",
            "lastReading": {
                "id": last_reading.id if last_reading else None,
                "sensor_id": last_reading.sensor_id if last_reading else None,
                "name": s.name,
                "value": last_reading.value if last_reading else None,
                "unit": s.unit,
                "timestamp": last_reading.timestamp.isoformat() if last_reading else None,
                "quality": "good",
            } if last_reading else None
        })
    return jsonify(result)


@sensors_bp.route("/<int:sensor_id>/readings", methods=["GET"])
@jwt_required()
@require_roles("admin", "agent")
def get_sensor_readings(sensor_id):
    limit = request.args.get("limit", 100, type=int)
    Sensor.query.get_or_404(sensor_id)
    data = (
        SensorData.query.filter_by(sensor_id=sensor_id)
        .order_by(SensorData.timestamp.desc())
        .limit(limit)
        .all()
    )
    return jsonify([{
        "id": d.id,
        "sensor_id": d.sensor_id,
        "name": d.sensor.name if d.sensor else None,
        "value": d.value,
        "unit": d.sensor.unit if d.sensor else None,
        "timestamp": d.timestamp.isoformat(),
        "quality": "good",
    } for d in reversed(data)])


@sensors_bp.route("/", methods=["POST"])
@jwt_required()
@require_roles("admin")
def create_sensor():
    data = request.json or {}
    sensor = Sensor(
        name=data.get("name"),
        category=data.get("category"),
        type=data.get("type"),
        unit=data.get("unit"),
        status=data.get("status", "active"),
        battery_level=data.get("battery_level", 100),
        zone=data.get("zone"),
        latitude=data.get("latitude"),
        longitude=data.get("longitude"),
        min_value=data.get("min_value"),
        max_value=data.get("max_value"),
    )
    db.session.add(sensor)
    db.session.commit()
    return jsonify({"message": "Sensor created", "id": sensor.id}), 201


@sensors_bp.route("/<int:sensor_id>", methods=["GET"])
@jwt_required()
@require_roles("admin", "agent")
def get_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    return jsonify({
        "id": sensor.id,
        "name": sensor.name,
        "category": sensor.category,
        "type": sensor.type,
        "unit": sensor.unit,
        "status": sensor.status,
        "battery_level": sensor.battery_level,
        "zone": sensor.zone,
        "latitude": sensor.latitude,
        "longitude": sensor.longitude,
        "min_value": sensor.min_value,
        "max_value": sensor.max_value,
    })


@sensors_bp.route("/<int:sensor_id>", methods=["PATCH", "PUT"])
@jwt_required()
@require_roles("admin")
def update_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    data = request.json or {}

    sensor.name = data.get("name", sensor.name)
    sensor.category = data.get("category", sensor.category)
    sensor.type = data.get("type", sensor.type)
    sensor.unit = data.get("unit", sensor.unit)
    sensor.status = data.get("status", sensor.status)
    sensor.battery_level = data.get("batteryLevel", sensor.battery_level)
    sensor.zone = data.get("zone", sensor.zone)
    sensor.latitude = data.get("latitude", sensor.latitude)
    sensor.longitude = data.get("longitude", sensor.longitude)
    sensor.min_value = data.get("min_value", sensor.min_value)
    sensor.max_value = data.get("max_value", sensor.max_value)

    db.session.commit()
    return get_sensor(sensor.id)


@sensors_bp.route("/<int:sensor_id>", methods=["DELETE"])
@jwt_required()
@require_roles("admin")
def delete_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    db.session.delete(sensor)
    db.session.commit()
    return jsonify({"message": "Sensor deleted"})


# ----------------------------
# SENSOR DATA CRUD
# ----------------------------
@sensors_bp.route("/<int:sensor_id>/data", methods=["GET"])
@jwt_required()
@require_roles("admin", "agent")
def get_sensor_data(sensor_id):
    Sensor.query.get_or_404(sensor_id)
    data = SensorData.query.filter_by(sensor_id=sensor_id).all()
    return jsonify([{
        "id": d.id,
        "value": d.value,
        "timestamp": d.timestamp.isoformat()
    } for d in data])


@sensors_bp.route("/<int:sensor_id>/data", methods=["POST"])
@jwt_required()
@require_roles("admin")
def add_sensor_data(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    data = request.json or {}

    sensor_data = SensorData(sensor_id=sensor_id, value=data["value"])
    db.session.add(sensor_data)

    # Vérifier seuils
    if sensor.min_value is not None and sensor_data.value < sensor.min_value:
        alert = Alert(
            message=f"Valeur trop basse ({sensor_data.value}{sensor.unit}) pour {sensor.name}",
            severity="low",
            sensor_id=sensor_id,
        )
        db.session.add(alert)

    if sensor.max_value is not None and sensor_data.value > sensor.max_value:
        alert = Alert(
            message=f"Valeur trop élevée ({sensor_data.value}{sensor.unit}) pour {sensor.name}",
            severity="high",
            sensor_id=sensor_id,
        )
        db.session.add(alert)

    db.session.commit()
    return jsonify({"message": "Data added", "id": sensor_data.id}), 201


@sensors_bp.route("/data/<int:data_id>", methods=["PUT"])
@jwt_required()
@require_roles("admin")
def update_sensor_data(data_id):
    sensor_data = SensorData.query.get_or_404(data_id)
    data = request.json or {}
    sensor_data.value = data.get("value", sensor_data.value)
    db.session.commit()
    return jsonify({"message": "Data updated"})


@sensors_bp.route("/data/<int:data_id>", methods=["DELETE"])
@jwt_required()
@require_roles("admin")
def delete_sensor_data(data_id):
    sensor_data = SensorData.query.get_or_404(data_id)
    db.session.delete(sensor_data)
    db.session.commit()
    return jsonify({"message": "Data deleted"})


# ----------------------------
# HISTORY
# ----------------------------
@sensors_bp.route("/history", methods=["GET"])
@jwt_required()
@require_roles("admin", "agent")
def get_sensor_history():
    limit = request.args.get("limit", default=500, type=int)
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(limit).all()
    return jsonify([{
        "id": d.id,
        "sensor_id": d.sensor_id,
        "name": d.sensor.name if d.sensor else None,
        "value": d.value,
        "unit": d.sensor.unit if d.sensor else None,
        "timestamp": d.timestamp.isoformat(),
    } for d in reversed(data)])
