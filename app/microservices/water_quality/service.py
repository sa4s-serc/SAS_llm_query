import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase

class WaterQualityParams(BaseModel):
    water_body_name: str

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
        water_body = params["water_body_name"]
        if water_body in self.water_quality_data:
            return {
                "water_body": water_body,
                "quality_data": self.water_quality_data[water_body][-1]  # Get the most recent data
            }
        else:
            raise HTTPException(status_code=404, detail="Water body not found")

def start_water_quality_service():
    service = WaterQualityService()
    service.run()

if __name__ == "__main__":
    start_water_quality_service()
