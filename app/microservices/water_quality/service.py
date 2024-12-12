import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase
from datetime import datetime

class WaterQualityParams(BaseModel):
    location: Optional[List[str]] = None
    timestamp: Optional[str] = None

class WaterQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("water_quality")
        self.update_service_info(
            description="Tracks water quality in lakes and other water bodies",
            dependencies=[]
        )
        self.water_quality_data = self.load_water_quality_data()

    def load_water_quality_data(self):
        try:
            with open('data/water_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("water_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding water_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/water_quality")
        async def get_water_quality(params: WaterQualityParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_data = self.water_quality_data

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
                "sensor1_value": closest_data.get('sensor1_value', 0.0),
                "sensor2_value": closest_data.get('sensor2_value', 0.0),
                "raw_values": closest_data.get('raw_values', [0.0, 0.0])
            })

        if not results:
            self.logger.warning("No water quality data found matching the criteria")
            return {
                "measurements": [],
                "message": "No water quality data found for the specified locations."
            }

        self.logger.info(f"Returning water quality data for {len(results)} locations")
        return {
            "measurements": results,
            "message": f"Found water quality data for {len(results)} locations."
        }

def start_water_quality_service():
    service = WaterQualityService()
    service.run()

if __name__ == "__main__":
    start_water_quality_service()
