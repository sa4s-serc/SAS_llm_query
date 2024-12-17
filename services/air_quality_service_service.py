import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class AirQualityData(BaseModel):
    location: str
    timestamp: str
    AQI: float
    PM2_5: Optional[float] = None
    PM10: Optional[float] = None
    NO2: Optional[float] = None
    O3: Optional[float] = None


class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality_service")
        self.update_service_info(
            description="Provides real-time and historical air quality measurements, including AQI, PM2.5, PM10, NO2, and O3 levels for different locations.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/air_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/air_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/air_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/air-quality/measurements")
        async def get_air_quality(location: str, timestamp: Optional[str] = None):
            result = self.process_request(location, timestamp)
            if not result:
                raise HTTPException(status_code=404, detail="Data not found")
            return result

    def process_request(self, location: str, timestamp: Optional[str]):
        filtered_data = [entry for entry in self.data if entry['location'] == location]
        if timestamp:
            filtered_data = [entry for entry in filtered_data if entry['timestamp'] <= timestamp]
        return filtered_data[-1] if filtered_data else None


def start_air_quality_service():
    service = AirQualityService()
    service.run()


if __name__ == "__main__":
    start_air_quality_service()
