from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sqlite3
from pymongo import MongoClient

logger = setup_logger("BookingService")


class BookingRequest(BaseModel):
    location: str
    start_time: str
    end_time: str


class QualityCheckRequest(BaseModel):
    location: str
    timestamp: str
    sensors: List[str]


class BookingService(MicroserviceBase):
    def __init__(self):
        super().__init__("booking_event_service")
        self.update_service_info(
            description="Handles booking events and quality checks",
            dependencies=["mongodb", "sqlite"],
        )
        self.mongo_client = MongoClient("mongodb://localhost:27017/")
        self.sensor_mapping = {
            "air": "Airsensordata",
            "water": "Watersensordata",
            "solar": "Solarsensordata",
            "room": "RoomMonitoringsensordata",
            "crowd": "CrowdMonitoringsensordata",
        }
        self._init_db()

    def _init_db(self):
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

    def register_routes(self):
        @self.app.post("/book_location")
        async def book_location(request: BookingRequest):
            return await self._book_location(request)

        @self.app.post("/check_availability")
        async def check_availability(request: BookingRequest):
            return await self._check_availability(request)

        @self.app.post("/check_quality")
        async def check_quality(request: QualityCheckRequest):
            return await self._check_quality(request)

        @self.app.get("/data")
        async def get_data():
            return {"display": "none"}

    async def _book_location(self, request: BookingRequest):
        if not self._is_available(request):
            raise HTTPException(
                status_code=409,
                detail="Location is already booked for the requested time",
            )

        quality_check = await self._check_quality(
            QualityCheckRequest(
                location=request.location,
                timestamp=request.start_time,
                sensors=["air", "room", "water", "crowd"],
            )
        )

        if not all(
            result == f"Quality is good at {request.location}"
            for result in quality_check["data"].values()
        ):
            raise HTTPException(
                status_code=409,
                detail="Air quality or room conditions are not suitable",
            )

        try:
            conn = sqlite3.connect("booking_data.db")
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO Bookings (location, start_time, end_time) VALUES (?, ?, ?)",
                (request.location, request.start_time, request.end_time),
            )
            conn.commit()
            conn.close()
            return {"status": "success", "message": "Location booked successfully"}
        except Exception as e:
            logger.error(f"An error occurred while booking: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def _check_availability(self, request: BookingRequest):
        return {"status": "success", "available": self._is_available(request)}

    def _is_available(self, request: BookingRequest) -> bool:
        try:
            conn = sqlite3.connect("booking_data.db")
            cursor = conn.cursor()
            cursor.execute(
                """SELECT COUNT(*) FROM Bookings
                WHERE location = ? AND
                    (start_time BETWEEN ? AND ? OR end_time BETWEEN ? AND ? OR
                     ? BETWEEN start_time AND end_time OR ? BETWEEN start_time AND end_time)""",
                (
                    request.location,
                    request.start_time,
                    request.end_time,
                    request.start_time,
                    request.end_time,
                    request.start_time,
                    request.end_time,
                ),
            )
            count = cursor.fetchone()[0]
            conn.close()
            return count == 0
        except Exception as e:
            logger.error(f"An error occurred while checking availability: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

    async def _check_quality(self, request: QualityCheckRequest):
        results = {}
        try:
            for sensor in request.sensors:
                sensor_name = self.sensor_mapping.get(sensor)
                if not sensor_name:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid sensor type: {sensor}"
                    )

                db = self.mongo_client["sensordatabaseversion2"]
                collection = db["sensordata"]
                document = collection.find_one(
                    {"_id": f"{sensor_name}_{request.timestamp}"}
                )

                if document and sensor_name in document:
                    sensor_data = document[sensor_name]
                    value_key = f"value{request.location[-1]}"
                    value = sensor_data.get(value_key, float("inf"))

                    results[sensor] = (
                        f"Quality is {'good' if value < 100 else 'bad'} at {request.location}"
                    )
                else:
                    results[sensor] = (
                        f"No data found for the specified timestamp and location {request.location}"
                    )

            return {"status": "success", "data": results}
        except Exception as e:
            logger.error(f"An error occurred while checking quality: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")


def start_booking_event_service():
    service = BookingService()
    service.run()


if __name__ == "__main__":
    start_booking_event_service()
