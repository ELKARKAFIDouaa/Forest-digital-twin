from app import create_app, db, socketio
from flask_migrate import Migrate
from app.services.sensor_service import start_sensor_thread

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    start_sensor_thread(app)   # Start fake data generator
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
