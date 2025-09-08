from flask import Blueprint, request, jsonify
from app import db
from app.models.sensor import Sensor
from app.models.sensor_data import SensorData

sensors_bp = Blueprint("sensors", __name__)

# ----------------------------
# SENSOR CRUD
# ----------------------------

# Create sensor
@sensors_bp.route("/sensors", methods=["POST"])
def create_sensor():
    data = request.json
    sensor = Sensor(
        name=data.get("name"),
        category=data.get("category"),
        type=data.get("type"),
        unit=data.get("unit"),
        interface=data.get("interface"),
        reference=data.get("reference")
    )
    db.session.add(sensor)
    db.session.commit()
    return jsonify({"message": "Sensor created", "id": sensor.id}), 201


# Get all sensors
@sensors_bp.route("/sensors", methods=["GET"])
def list_sensors():
    sensors = Sensor.query.all()
    return jsonify([{
        "id": s.id,
        "name": s.name,
        "category": s.category,
        "type": s.type,
        "unit": s.unit,
        "interface": s.interface,
        "reference": s.reference
    } for s in sensors])


# Get single sensor
@sensors_bp.route("/sensors/<int:sensor_id>", methods=["GET"])
def get_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    return jsonify({
        "id": sensor.id,
        "name": sensor.name,
        "category": sensor.category,
        "type": sensor.type,
        "unit": sensor.unit,
        "interface": sensor.interface,
        "reference": sensor.reference
    })


# Update sensor
@sensors_bp.route("/sensors/<int:sensor_id>", methods=["PUT"])
def update_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    data = request.json

    sensor.name = data.get("name", sensor.name)
    sensor.category = data.get("category", sensor.category)
    sensor.type = data.get("type", sensor.type)
    sensor.unit = data.get("unit", sensor.unit)
    sensor.interface = data.get("interface", sensor.interface)
    sensor.reference = data.get("reference", sensor.reference)

    db.session.commit()
    return jsonify({"message": "Sensor updated"})


# Delete sensor
@sensors_bp.route("/sensors/<int:sensor_id>", methods=["DELETE"])
def delete_sensor(sensor_id):
    sensor = Sensor.query.get_or_404(sensor_id)
    db.session.delete(sensor)
    db.session.commit()
    return jsonify({"message": "Sensor deleted"})


# ----------------------------
# SENSOR DATA CRUD
# ----------------------------

# Add simulated data
@sensors_bp.route("/sensors/<int:sensor_id>/data", methods=["POST"])
def add_sensor_data(sensor_id):
    Sensor.query.get_or_404(sensor_id)  # ensure sensor exists
    data = request.json
    sensor_data = SensorData(sensor_id=sensor_id, value=data["value"])
    db.session.add(sensor_data)
    db.session.commit()
    return jsonify({"message": "Data added", "id": sensor_data.id}), 201


# Get all data for a sensor
@sensors_bp.route("/sensors/<int:sensor_id>/data", methods=["GET"])
def get_sensor_data(sensor_id):
    Sensor.query.get_or_404(sensor_id)
    data = SensorData.query.filter_by(sensor_id=sensor_id).all()
    return jsonify([{
        "id": d.id,
        "value": d.value,
        "timestamp": d.timestamp
    } for d in data])


# Update a data record
@sensors_bp.route("/sensors/data/<int:data_id>", methods=["PUT"])
def update_sensor_data(data_id):
    sensor_data = SensorData.query.get_or_404(data_id)
    data = request.json
    sensor_data.value = data.get("value", sensor_data.value)
    db.session.commit()
    return jsonify({"message": "Data updated"})


# Delete a data record
@sensors_bp.route("/sensors/data/<int:data_id>", methods=["DELETE"])
def delete_sensor_data(data_id):
    sensor_data = SensorData.query.get_or_404(data_id)
    db.session.delete(sensor_data)
    db.session.commit()
    return jsonify({"message": "Data deleted"})

# Get History Data
@sensors_bp.route("/history", methods=["GET"])
def get_history():
    """
    Returns the latest N sensor data records across all sensors,
    oldest → newest.
    """
    limit = request.args.get("limit", default=500, type=int)

    # Query latest records
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(limit).all()

    # Return oldest → newest with ISO timestamps
    return jsonify([{
        "id": d.id,
        "sensor_id": d.sensor_id,
        "name": d.sensor.name,
        "value": d.value,
        "unit": d.sensor.unit,
        "timestamp": d.timestamp.isoformat()
    } for d in reversed(data)])



# ----------------------------
# HISTORY ENDPOINT
# ----------------------------
@sensors_bp.route("/history", methods=["GET"])
def get_sensor_history():
    """
    Returns the latest N sensor data records across all sensors,
    ordered from oldest → newest.
    """
    limit = request.args.get("limit", default=500, type=int)

    # Get latest records
    data = SensorData.query.order_by(SensorData.timestamp.desc()).limit(limit).all()

    # Reverse to make oldest → newest
    results = [{
        "id": d.id,
        "sensor_id": d.sensor_id,
        "name": d.sensor.name if d.sensor else None,
        "value": d.value,
        "unit": d.sensor.unit if d.sensor else None,
        "timestamp": d.timestamp.isoformat()
    } for d in reversed(data)]

    return jsonify(results)
