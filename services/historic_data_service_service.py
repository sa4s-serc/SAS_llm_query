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
            description="Service to provide historical details for sites",
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
        @self.app.post("/historic_sites/", response_model=List[HistoricSite])
        async def get_historic_sites(site_names: Optional[List[str]]):
            return self.process_request(site_names)

    def process_request(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="No site names provided")

        results = []
        for name in site_names:
            site_info = self.data.get(name)
            if site_info:
                results.append(HistoricSite(**site_info))
            else:
                self.logger.warning(f"Site {name} not found in data.")
        return results


def start_service_name():
    service = HistoricDataService()
    service.register_routes()
    service.run()


if __name__ == "__main__":
    start_service_name()
