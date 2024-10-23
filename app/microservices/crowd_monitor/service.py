import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase
from datetime import datetime

class CrowdMonitorParams(BaseModel):
    location: str
    timestamp: Optional[str] = None

class CrowdMonitorService(MicroserviceBase):
    def __init__(self):
        super().__init__("crowd_monitor")
        self.update_service_info(
            description="Tracks and reports real-time crowd density at various locations",
            dependencies=[]
        )
        self.crowd_data = self.load_crowd_data()

    def load_crowd_data(self):
        with open('data/crowd_quality_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/crowd_monitor")
        async def get_crowd_info(params: CrowdMonitorParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        location = params['location']
        timestamp = params.get('timestamp', datetime.now().isoformat())

        location_data = [data for data in self.crowd_data if data['location'] == location]
        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found")

        # Find the closest timestamp
        closest_data = min(location_data, key=lambda x: abs(datetime.fromisoformat(x['timestamp']) - datetime.fromisoformat(timestamp)))

        return {
            "location": location,
            "timestamp": closest_data['timestamp'],
            "crowd_count": closest_data['crowd_count']
        }

def start_crowd_monitor_service():
    service = CrowdMonitorService()
    service.run()

if __name__ == "__main__":
    start_crowd_monitor_service()
