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
            description="Service to provide real-time and historical air quality measurements.",
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
        async def get_air_quality(locations: List[str], timestamp: Optional[str] = None):
            return self.process_request(locations, timestamp)

    def process_request(self, locations: List[str], timestamp: Optional[str]):
        results = []
        for location in locations:
            filtered_data = [entry for entry in self.data if entry['location'] == location]
            if timestamp:
                filtered_data = sorted(filtered_data, key=lambda x: x['timestamp'])
                filtered_data = [entry for entry in filtered_data if entry['timestamp'] <= timestamp]
            if filtered_data:
                results.append(filtered_data[-1])  # Get the closest entry
            else:
                self.logger.warning(f"No data found for location: {location}")
                results.append({"location": location, "error": "No data found"})
        return results


def start_air_quality_service():
    service = AirQualityService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_air_quality_service()
