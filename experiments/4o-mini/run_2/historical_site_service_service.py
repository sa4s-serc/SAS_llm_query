import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class HistoricData(BaseModel):
    name: str
    year_built: str
    significance: str
    cultural_importance: str
    location: str
    description: str

class HistoricalSiteService(MicroserviceBase):
    def __init__(self):
        super().__init__("historical_site_service")
        self.update_service_info(
            description="Service to provide historical and cultural information about monuments and sites",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/historic_data.json not found")
            return {}
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return {}

    def register_routes(self):
        @self.app.post("/historical_sites/")
        async def get_historical_sites(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="Site names must be provided")

        results = {}
        for name in site_names:
            site_info = self.data.get(name)
            if site_info:
                results[name] = site_info
            else:
                results[name] = "Site not found"
        return results

def start_historical_site_service():
    service = HistoricalSiteService()
    service.run()

if __name__ == "__main__":
    start_historical_site_service()
