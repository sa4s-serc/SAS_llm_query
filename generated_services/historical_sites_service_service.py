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

class HistoricalSitesService(MicroserviceBase):
    def __init__(self):
        super().__init__("historical_sites_service")
        self.update_service_info(
            description="Service providing historical and cultural information about monuments and sites",
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
        @self.app.post("/get_historical_info/")
        async def get_historical_info(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="Site names must be provided.")

        results = {}
        for site in site_names:
            if site in self.data:
                results[site] = self.data[site]
            else:
                results[site] = "Site not found."
        return results

def start_historical_sites_service():
    service = HistoricalSitesService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_historical_sites_service()
