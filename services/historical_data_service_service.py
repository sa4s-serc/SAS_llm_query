import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class HistoricalSite(BaseModel):
    name: str
    year_built: str
    significance: str
    cultural_importance: str
    location: str
    description: str


class HistoricalDataService(MicroserviceBase):
    def __init__(self):
        super().__init__("historical_data_service")
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
            return {}  # Return an empty dictionary
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return {}  # Return an empty dictionary

    def register_routes(self):
        @self.app.post("/historical_sites/")
        async def get_historical_sites(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="No site names provided.")

        result = {}  # To store the results
        for site_name in site_names:
            site_info = self.data.get(site_name)
            if site_info:
                result[site_name] = site_info
            else:
                result[site_name] = "Site not found"
        return result


def start_historical_data_service():
    service = HistoricalDataService()
    service.register_routes()
    service.run()


if __name__ == "__main__":
    start_historical_data_service()
