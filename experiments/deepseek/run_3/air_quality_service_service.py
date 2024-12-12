import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class AirQualityRequest(BaseModel):
    locations: List[str]
    timestamp: Optional[str] = None


class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality_service")
        self.update_service_info(
            description="Provides real-time and historical air quality measurements including AQI, PM2.5, PM10, NO2, and O3 levels for different locations.",
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
        async def get_air_quality(request: AirQualityRequest):
            return self.process_request(request)

    def process_request(self, request: AirQualityRequest):
        results = []
        for location in request.locations:
            matching_data = [item for item in self.data if item["location"] == location]
            if request.timestamp:
                matching_data = [item for item in matching_data if item["timestamp"] == request.timestamp]
            if matching_data:
                results.append(matching_data[0])
            else:
                results.append({"location": location, "message": "No data found for this location."})
        return results


def start_air_quality_service():
    service = AirQualityService()
    service.run()


if __name__ == "__main__":
    start_air_quality_service()
