import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class WaterQualityData(BaseModel):
    location: str
    timestamp: str
    pH: float
    Dissolved_Oxygen: float
    Conductivity: float
    Turbidity: float
    Temperature: float

class WaterQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("water_quality_service")
        self.update_service_info(
            description="Service to monitor water quality metrics in different locations",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/water_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/water_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/water_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/water-quality/")
        async def get_water_quality(location: str, timestamp: Optional[str] = None):
            return self.process_request(location, timestamp)

    def process_request(self, location: str, timestamp: Optional[str]):
        filtered_data = [entry for entry in self.data if entry['location'] == location]
        if not filtered_data:
            raise HTTPException(status_code=404, detail="Location not found")

        if timestamp:
            filtered_data = [entry for entry in filtered_data if entry['timestamp'] <= timestamp]

        if not filtered_data:
            raise HTTPException(status_code=404, detail="No data found for the given timestamp")

        closest_entry = max(filtered_data, key=lambda x: x['timestamp'])
        return closest_entry

def start_service_name():
    service = WaterQualityService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_service_name()
