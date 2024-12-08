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
        super().__init__("water_quality")  # service name without _service suffix
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
        @self.app.post("/water_quality")
        async def get_water_quality(location: str, timestamp: Optional[str] = None):
            response = self.process_request(location, timestamp)
            if response is None:
                raise HTTPException(status_code=404, detail="No data found for the given location and timestamp")
            return response

    def process_request(self, location: str, timestamp: Optional[str]):
        filtered_data = [
            entry for entry in self.data 
            if entry['location'] == location
        ]
        if timestamp:
            # Sort by timestamp and find the closest
            filtered_data.sort(key=lambda x: abs(pd.to_datetime(x['timestamp']) - pd.to_datetime(timestamp)))
        if filtered_data:
            return filtered_data[0]  # Return the closest entry
        return None

    def start_service(self):
        self.register_routes()
        self.run()

def start_water_quality():
    service = WaterQualityService()
    service.start_service()

if __name__ == "__main__":
    start_water_quality()
