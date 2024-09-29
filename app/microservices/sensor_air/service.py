# room_sensor.py
from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
from fastapi import HTTPException, Body
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
import psutil
import atexit

logger = setup_logger("SensorAirService")


class SensorData(BaseModel):
    Name: str
    Time: str
    Sensor1: float
    Sensor2: float
    Sensor1Location: str
    Sensor2Location: str


class SensorAirService(MicroserviceBase):
    def __init__(self):
        super().__init__("sensor_air_service")
        self.update_service_info(
            description="Handles air sensor data and notifications",
            dependencies=["mongodb"],
        )

    def register_routes(self):
        @self.app.post("/notification")
        async def handle_notification(data: SensorData):
            return await self._handle_notification(data)

        @self.app.get("/get_data/{id}")
        async def get_data(id: str):
            return await self._get_data(id)

        @self.app.get("/data")
        async def get_data():
            return {"display": "none"}

    async def _handle_notification(self, data: SensorData):
        try:
            self._store_to_mongodb_sensor(
                db_name="room_sensor_db",
                collection_name="roomsensordata",
                sensor_name=data.Name,
                timestamp=data.Time,
                sensor1_data={"data": data.Sensor1, "location": data.Sensor1Location},
                sensor2_data={"data": data.Sensor2, "location": data.Sensor2Location},
            )
            return {"status": "success", "message": "Data stored successfully"}
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    async def _get_data(self, id: str):
        try:
            data = self._fetch_from_mongodb("room_sensor_db", "roomsensordata", id)
            if data:
                return {"status": "success", "data": data}
            else:
                raise HTTPException(status_code=404, detail="Data not found")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def _fetch_from_mongodb(self, db_name, collection_name, id):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client[db_name]
            collection = db[collection_name]
            data = collection.find_one({"_id": id}, {"_id": 0})
            return data
        except Exception as e:
            logger.error(f"Error fetching data from MongoDB: {e}")
            return None

    def _store_to_mongodb_sensor(
        self,
        db_name,
        collection_name,
        sensor_name,
        timestamp,
        sensor1_data,
        sensor2_data,
    ):
        try:
            client = MongoClient("mongodb://localhost:27017/")
            db = client[db_name]
            collection = db[collection_name]
            sensor_data = {"sensor1": sensor1_data, "sensor2": sensor2_data}
            update_data = {sensor_name: sensor_data}
            collection.update_one(
                {"_id": timestamp}, {"$set": update_data}, upsert=True
            )

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(
                f"Data stored successfully for {sensor_name} at {timestamp}. Current time: {current_time}"
            )
        except Exception as e:
            logger.error(f"Error storing data to MongoDB: {e}")

    def _print_cpu_usage(self):
        cpu_times = self.process.cpu_times()
        logger.info(
            f"Total CPU time used by the program (in seconds): User = {cpu_times.user}, System = {cpu_times.system}"
        )


def start_sensor_air_service():
    service = SensorAirService()
    service.run()


if __name__ == "__main__":
    start_sensor_air_service()
