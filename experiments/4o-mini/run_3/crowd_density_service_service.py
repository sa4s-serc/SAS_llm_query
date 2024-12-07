import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class CrowdData(BaseModel):
    location: str
    timestamp: str
    crowd_count: int

class CrowdDensityService(MicroserviceBase):
    def __init__(self):
        super().__init__("crowd_density_service")
        self.update_service_info(
            description="Service to monitor crowd density at different locations.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/crowd_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/crowd_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/crowd_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/crowd_density/")
        async def get_crowd_density(location: str, timestamp: Optional[str] = None):
            return self.process_request(location, timestamp)

    def process_request(self, location: str, timestamp: Optional[str]):
        filtered_data = [entry for entry in self.data if entry['location'] == location]
        if not filtered_data:
            raise HTTPException(status_code=404, detail="Location not found")
        if timestamp:
            filtered_data = [entry for entry in filtered_data if entry['timestamp'] <= timestamp]
        if not filtered_data:
            raise HTTPException(status_code=404, detail="No crowd data found for the given timestamp")
        closest_entry = max(filtered_data, key=lambda x: x['timestamp'])  # Get the closest timestamp
        return {"location": closest_entry['location'], "timestamp": closest_entry['timestamp'], "crowd_count": closest_entry['crowd_count']}

def start_service_name():
    service = CrowdDensityService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_service_name()
