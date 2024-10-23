import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase
from datetime import datetime

class WaterQualityParams(BaseModel):
    location: str
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
        with open('data/water_quality_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/water_quality")
        async def get_water_quality(params: WaterQualityParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        location = params['location']
        timestamp = params.get('timestamp', datetime.now().isoformat())

        location_data = [data for data in self.water_quality_data if data['location'] == location]
        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found")

        # Find the closest timestamp
        closest_data = min(location_data, key=lambda x: abs(datetime.fromisoformat(x['timestamp']) - datetime.fromisoformat(timestamp)))

        return {
            "location": location,
            "timestamp": closest_data['timestamp'],
            "pH": closest_data['pH'],
            "Dissolved_Oxygen": closest_data['Dissolved_Oxygen'],
            "Conductivity": closest_data['Conductivity'],
            "Turbidity": closest_data['Turbidity'],
            "Temperature": closest_data['Temperature']
        }

def start_water_quality_service():
    service = WaterQualityService()
    service.run()

if __name__ == "__main__":
    start_water_quality_service()
