import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase

class HistoricalInfoParams(BaseModel):
    site_name: str

class HistoricalInfoService(MicroserviceBase):
    def __init__(self):
        super().__init__("historical_info")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and sites",
            dependencies=[]
        )
        self.historical_data = self.load_historical_data()

    def load_historical_data(self):
        with open('data/historic_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/historical_info")
        async def get_historical_info(params: HistoricalInfoParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        site_name = params["site_name"]
        if site_name in self.historical_data:
            site_info = self.historical_data[site_name]
            return {"name": site_info["name"], "body": site_info["body"]}
        else:
            raise HTTPException(status_code=404, detail="Site not found")

def start_historical_info_service():
    service = HistoricalInfoService()
    service.run()

if __name__ == "__main__":
    start_historical_info_service()
