import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from app.microservices.base import MicroserviceBase

class AirQualityParams(BaseModel):
    locations: List[str]

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
        locations = params["locations"]
        result = {}
        for location in locations:
            if location in self.air_quality_data:
                result[location] = self.air_quality_data[location][-1]  # Get the most recent data
            else:
                result[location] = None
        return result

def start_air_quality_service():
    service = AirQualityService()
    service.run()

if __name__ == "__main__":
    start_air_quality_service()
