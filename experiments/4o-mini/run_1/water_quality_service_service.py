import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class WaterQualityData(BaseModel):
    location: str
    timestamp: str
    pH: Optional[float]
    Dissolved_Oxygen: Optional[float]
    Conductivity: Optional[float]
    Turbidity: Optional[float]
    Temperature: Optional[float]

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
        filtered_data = [
            record for record in self.data
            if record['location'] == location
        ]
        if timestamp:
            filtered_data = [
                record for record in filtered_data
                if record['timestamp'] <= timestamp
            ]
        if not filtered_data:
            raise HTTPException(status_code=404, detail="No data found for the given location and timestamp.")
        # Find the nearest timestamp if multiple records exist
        filtered_data.sort(key=lambda x: x['timestamp'], reverse=True)
        return filtered_data[0]  # Return the most recent record

def start_service_name():
    service = WaterQualityService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_service_name()
