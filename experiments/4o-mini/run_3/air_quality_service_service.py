import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class AirQualityData(BaseModel):
    location: str
    timestamp: str
    AQI: Optional[float]
    PM2_5: Optional[float] = None
    PM10: Optional[float] = None
    NO2: Optional[float] = None
    O3: Optional[float] = None


class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality_service")
        self.update_service_info(
            description="Provides real-time and historical air quality measurements",
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
        @self.app.post("/get-air-quality/")
        async def get_air_quality(locations: List[str], timestamp: Optional[str] = None):
            results = self.process_request(locations, timestamp)
            if not results:
                raise HTTPException(status_code=404, detail="No data found for the requested locations and timestamp.")
            return results

    def process_request(self, locations: List[str], timestamp: Optional[str]):
        filtered_data = []
        for entry in self.data:
            if entry['location'] in locations:
                if timestamp:
                    if entry['timestamp'] == timestamp:
                        filtered_data.append(entry)
                else:
                    filtered_data.append(entry)
        return filtered_data


def start_air_quality_service():
    service = AirQualityService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_air_quality_service()
