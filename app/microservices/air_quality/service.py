import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase
from datetime import datetime

class AirQualityParams(BaseModel):
    location: str
    timestamp: Optional[str] = None

class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality")
        self.update_service_info(
            description="Monitors and reports air quality levels in different areas",
            dependencies=[]
        )
        self.air_quality_data = self.load_air_quality_data()

    def load_air_quality_data(self):
        with open('data/air_quality_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/air_quality")
        async def get_air_quality(params: AirQualityParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        location = params['location']
        timestamp = params.get('timestamp', datetime.now().isoformat())

        location_data = [data for data in self.air_quality_data if data['location'] == location]
        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found")

        # Find the closest timestamp
        closest_data = min(location_data, key=lambda x: abs(datetime.fromisoformat(x['timestamp']) - datetime.fromisoformat(timestamp)))

        return {
            "location": location,
            "timestamp": closest_data['timestamp'],
            "AQI": closest_data['AQI'],
            "PM2.5": closest_data['PM2.5'],
            "PM10": closest_data['PM10'],
            "NO2": closest_data['NO2'],
            "O3": closest_data['O3']
        }

def start_air_quality_service():
    service = AirQualityService()
    service.run()

if __name__ == "__main__":
    start_air_quality_service()
