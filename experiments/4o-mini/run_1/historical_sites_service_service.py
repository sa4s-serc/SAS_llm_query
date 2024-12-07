import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class SiteDetails(BaseModel):
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
            description="Provides historical and cultural information about monuments and sites.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/historic_data.json not found")
            return {}  # return an empty dict
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return {}  # return an empty dict

    def register_routes(self):
        @self.app.post("/get_site_details/")
        async def get_site_details(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="No site names provided")
        results = {}
        for name in site_names:
            if name in self.data:
                results[name] = self.data[name]
            else:
                results[name] = "Site not found"
        return results

def start_historical_sites_service():
    service = HistoricalSitesService()
    service.run()

if __name__ == "__main__":
    start_historical_sites_service()
