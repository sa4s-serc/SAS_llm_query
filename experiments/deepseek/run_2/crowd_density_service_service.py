import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class CrowdDataRequest(BaseModel):
    location: str
    timestamp: Optional[str] = None

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
        def get_crowd_density(request: CrowdDataRequest):
            return self.process_request(request)

    def process_request(self, request: CrowdDataRequest):
        location = request.location
        timestamp = request.timestamp
        matching_data = [item for item in self.data if item['location'] == location]
        if not matching_data:
            raise HTTPException(status_code=404, detail="Location not found")
        if timestamp:
            closest_match = min(matching_data, key=lambda x: abs(self.parse_timestamp(x['timestamp']) - self.parse_timestamp(timestamp)))
        else:
            closest_match = max(matching_data, key=lambda x: self.parse_timestamp(x['timestamp']))
        return closest_match['crowd_count']

    def parse_timestamp(self, timestamp: str) -> float:
        from datetime import datetime
        return datetime.fromisoformat(timestamp).timestamp()

    def start_crowd_density_service():
        service = CrowdDensityService()
        service.run()

    if __name__ == "__main__":
        start_crowd_density_service()
