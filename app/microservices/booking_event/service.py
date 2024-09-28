import sqlite3
from flask import Flask, request, jsonify
from app.utils.logger import setup_logger
from pymongo import MongoClient

logger = setup_logger("BookingService")

mongo_client = MongoClient("mongodb://localhost:27017/")
# Define sensor mapping globally
sensor_mapping = {
    "air": "Airsensordata",
    "water": "Watersensordata",
    "solar": "Solarsensordata",
    "room": "RoomMonitoringsensordata",
    "crowd": "CrowdMonitoringsensordata",
}


# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("booking_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS Bookings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        location TEXT,
                        start_time TEXT,
                        end_time TEXT
                      )"""
    )
    conn.commit()
    conn.close()


init_db()


class BookingService:
    def __init__(self):
        self.app = Flask(__name__)

        @self.app.route("/book_location", methods=["POST"])
        def book_location():
            return self._book_location()

        @self.app.route("/check_availability", methods=["POST"])
        def check_availability():
            return self._check_availability()

        @self.app.route("/check_quality", methods=["POST"])
        def check_quality():
            return self._check_quality()

    def _book_location(self):
        data = request.json
        location = data.get("location")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not location or not start_time or not end_time:
            return (
                jsonify({"status": "error", "message": "Missing required fields"}),
                400,
            )

        # Step 1: Check availability
        availability_response = self._check_availability_internal(data)
        if availability_response["status"] != "success":
            return jsonify(availability_response), 409

        # Step 2: Check air quality and room monitoring data
        quality_check_data = {
            "location": location,
            "timestamp": start_time,
            "sensors": ["air", "room", "water", "crowd"],
        }
        quality_response = self._check_quality_internal(quality_check_data)
        quality_results = quality_response.get("data", {})

        if (
            quality_results.get("air") != f"Quality is good at {location}"
            or quality_results.get("room") != f"Quality is good at {location}"
        ):
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "Air quality or room conditions are not suitable",
                    }
                ),
                409,
            )

        # Step 3: Book the location
        try:
            conn = sqlite3.connect("booking_data.db")
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO Bookings (location, start_time, end_time) VALUES (?, ?, ?)""",
                (location, start_time, end_time),
            )
            conn.commit()
            conn.close()
            return (
                jsonify(
                    {"status": "success", "message": "Location booked successfully"}
                ),
                200,
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500

    def _check_availability(self):
        data = request.json
        return self._check_availability_internal(data)

    def _check_availability_internal(self, data):
        location = data.get("location")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not location or not start_time or not end_time:
            return {"status": "error", "message": "Missing required fields"}

        try:
            conn = sqlite3.connect("booking_data.db")
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM Bookings
                              WHERE location = ? AND
                                    (start_time BETWEEN ? AND ? OR end_time BETWEEN ? AND ? OR
                                     ? BETWEEN start_time AND end_time OR ? BETWEEN start_time AND end_time)""",
                (
                    location,
                    start_time,
                    end_time,
                    start_time,
                    end_time,
                    start_time,
                    end_time,
                ),
            )
            count = cursor.fetchone()[0]
            conn.close()
            if count > 0:
                return {
                    "status": "error",
                    "message": "Location is already booked for the requested time",
                }
            else:
                return {"status": "success", "message": "Location is available"}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"status": "error", "message": str(e)}

    def _check_quality(self):
        data = request.json
        return self._check_quality_internal(data)

    def _check_quality_internal(self, data):
        sensors = data.get("sensors")
        timestamp = data.get("timestamp")
        location = data.get("location")

        if not sensors or not timestamp or not location:
            return {"status": "error", "message": "Missing required fields"}

        results = {}
        try:
            for sensor in sensors:
                sensor_name = sensor_mapping.get(sensor)
                if not sensor_name:
                    return {
                        "status": "error",
                        "message": f"Invalid sensor type: {sensor}",
                    }

                # Assuming `mongo_client` is already connected to MongoDB
                db = mongo_client["sensordatabaseversion2"]
                collection = db["sensordata"]
                document = collection.find_one({"_id": f"{sensor_name}_{timestamp}"})

                if document and sensor_name in document:
                    sensor_data = document[sensor_name]
                    value_key = f"value{location[-1]}"  # Assuming location is in format 'room1', 'room2', etc.
                    value = sensor_data.get(value_key, float("inf"))

                    if value < 100:
                        results[sensor] = f"Quality is good at {location}"
                    else:
                        results[sensor] = f"Quality is bad at {location}"
                else:
                    results[sensor] = (
                        f"No data found for the specified timestamp and location {location}"
                    )

            return {"status": "success", "data": results}
        except Exception as e:
            print(f"An error occurred: {e}")
            return {"status": "error", "message": str(e)}

    def run(self):
        self.app.run(port=8000)


def start_booking_event_service():
    service = BookingService()
    service.run()


if __name__ == "__main__":
    start_booking_service()
