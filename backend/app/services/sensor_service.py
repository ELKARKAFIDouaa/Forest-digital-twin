from app import db, socketio
from app.models.sensor import Sensor
from app.models.sensor_data import SensorData
from datetime import datetime
import random
import threading
import time

def generate_sensor_data(app):
    with app.app_context():  # Toujours travailler dans le contexte app
        while True:
            sensors = Sensor.query.all()
            for s in sensors:
                value = round(random.uniform(10, 30), 2)  # exemple pour température
                data = SensorData(sensor_id=s.id, value=value, timestamp=datetime.utcnow())
                db.session.add(data)
                db.session.commit()
                socketio.emit("sensor_data", {
                    "sensor_id": s.id,
                    "name": s.name,
                    "value": value,
                    "unit": s.unit,
                    "timestamp": data.timestamp.isoformat()
                })

            time.sleep(5)  # toutes les 5 secondes

def start_sensor_thread(app):
    thread = threading.Thread(target=generate_sensor_data, args=(app,))
    thread.daemon = True
    thread.start()
