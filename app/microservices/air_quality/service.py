import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase
from datetime import datetime

class AirQualityParams(BaseModel):
    location: Optional[List[str]] = None
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
        try:
            with open('data/air_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("air_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding air_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/air_quality")
        async def get_air_quality(params: AirQualityParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_data = self.air_quality_data

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
                "AQI": closest_data['AQI'],
                "PM2.5": closest_data['PM2.5'],
                "PM10": closest_data['PM10'],
                "NO2": closest_data['NO2'],
                "O3": closest_data['O3']
            })

        if not results:
            self.logger.warning("No air quality data found matching the criteria")
            return {
                "measurements": [],
                "message": "No air quality data found for the specified locations."
            }

        self.logger.info(f"Returning air quality data for {len(results)} locations")
        return {
            "measurements": results,
            "message": f"Found air quality data for {len(results)} locations."
        }

def start_air_quality_service():
    service = AirQualityService()
    service.run()

if __name__ == "__main__":
    start_air_quality_service()
