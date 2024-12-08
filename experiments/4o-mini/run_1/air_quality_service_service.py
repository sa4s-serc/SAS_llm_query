import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class AirQualityData(BaseModel):
    location: str
    timestamp: str
    AQI: float
    PM2_5: float
    PM10: float
    NO2: float
    O3: float


class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality_service")
        self.update_service_info(
            description="Service to provide real-time and historical air quality measurements",
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
        @self.app.post("/air_quality")
        async def get_air_quality(locations: Optional[List[str]], timestamp: Optional[str] = None):
            result = self.process_request(locations, timestamp)
            if not result:
                raise HTTPException(status_code=404, detail="No data found for the provided parameters")
            return result

    def process_request(self, locations: Optional[List[str]], timestamp: Optional[str] = None):
        if not locations:
            return []
        filtered_data = [
            entry for entry in self.data 
            if entry['location'] in locations
        ]
        # Optionally filter by timestamp if provided
        if timestamp:
            filtered_data = [
                entry for entry in filtered_data 
                if entry['timestamp'] <= timestamp
            ]
        return filtered_data


def start_air_quality_service():
    service = AirQualityService()
    service.register_routes()
    service.run()


if __name__ == "__main__":
    start_air_quality_service()
