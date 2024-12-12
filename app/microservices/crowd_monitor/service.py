import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase
from datetime import datetime

class CrowdMonitorParams(BaseModel):
    location: Optional[List[str]] = None
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
        try:
            with open('data/crowd_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("crowd_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding crowd_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/crowd_monitor")
        async def get_crowd_info(params: CrowdMonitorParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_data = self.crowd_data

        if params.get('location'):
            locations = params['location']
            if isinstance(locations, str):
                locations = [locations]
            filtered_data = [d for d in filtered_data if d['location'] in locations]
            self.logger.info(f"After location filter: {len(filtered_data)} measurements")

        timestamp = params.get('timestamp', datetime.now().isoformat())
        
        # Group data by location
        location_data = {}
        for data in filtered_data:
            loc = data['location']
            if loc not in location_data:
                location_data[loc] = []
            location_data[loc].append(data)

        # Get latest readings for each location
        results = []
        for loc, measurements in location_data.items():
            closest_data = min(measurements, 
                             key=lambda x: abs(datetime.fromisoformat(x['timestamp']) - datetime.fromisoformat(timestamp)))
            results.append({
                "location": loc,
                "timestamp": closest_data['timestamp'],
                "crowd_count": closest_data['crowd_count']
            })

        if not results:
            self.logger.warning("No crowd data found matching the criteria")
            return {
                "measurements": [],
                "message": "No crowd data found for the specified locations."
            }

        self.logger.info(f"Returning crowd data for {len(results)} locations")
        return {
            "measurements": results,
            "message": f"Found crowd data for {len(results)} locations."
        }

def start_crowd_monitor_service():
    service = CrowdMonitorService()
    service.run()

if __name__ == "__main__":
    start_crowd_monitor_service()
