import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class HistoricSite(BaseModel):
    name: str
    year_built: str
    significance: str
    cultural_importance: str
    location: str
    description: str


class HistoricDataService(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_data_service")
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
        @self.app.post("/historic_sites")
        async def get_historic_sites(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="Please provide at least one site name.")

        results = {}
        for site_name in site_names:
            site_info = self.data.get(site_name)
            if site_info:
                results[site_name] = site_info
            else:
                results[site_name] = "Site not found."
        return results


def start_historic_data_service():
    service = HistoricDataService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_historic_data_service()
