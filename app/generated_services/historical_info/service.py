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

class ServiceHistoricData(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_data")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and historical sites.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/historic_data.json not found")
            return {}  # returning empty dict based on the data structure
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return {}  # returning empty dict based on the data structure

    def register_routes(self):
        @self.app.post("/historic_data")
        async def get_historic_data(site_names: Optional[List[str]]):
            if not site_names:
                raise HTTPException(status_code=400, detail="No site names provided.")
            results = self.process_request(site_names)
            return results

    def process_request(self, site_names: List[str]):
        results = {}
        for site in site_names:
            if site in self.data:
                results[site] = self.data[site]
            else:
                results[site] = "Site not found."
        return results

def start_service_name():
    service = ServiceHistoricData()
    service.run()

if __name__ == '__main__':
    start_service_name()
