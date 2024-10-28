import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class HistoricalInfoParams(BaseModel):
    site_name: Optional[List[str]] = None

class HistoricalInfoService(MicroserviceBase):
    def __init__(self):
        super().__init__("historical_info")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and sites",
            dependencies=[]
        )
        self.historical_data = self.load_historical_data()

    def load_historical_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("historic_data.json not found")
            return {}
        except json.JSONDecodeError:
            self.logger.error("Error decoding historic_data.json")
            return {}

    def register_routes(self):
        @self.app.post("/historical_info")
        async def get_historical_info(params: HistoricalInfoParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        results = []

        if params.get('site_name'):
            site_names = params['site_name']
            if isinstance(site_names, str):
                site_names = [site_names]
            
            for site in site_names:
                if site in self.historical_data:
                    results.append(self.historical_data[site])
                    self.logger.info(f"Found information for site: {site}")
                else:
                    self.logger.warning(f"No information found for site: {site}")

        if not results:
            self.logger.warning("No historical information found")
            return {
                "sites": [],
                "message": "No historical information found for the specified sites."
            }

        self.logger.info(f"Returning information for {len(results)} sites")
        return {
            "sites": results,
            "message": f"Found historical information for {len(results)} sites."
        }

def start_historical_info_service():
    service = HistoricalInfoService()
    service.run()

if __name__ == "__main__":
    start_historical_info_service()
