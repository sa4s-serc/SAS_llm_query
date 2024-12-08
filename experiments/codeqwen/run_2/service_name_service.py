import json
from fastapi import HTTPException
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

class ServiceName(MicroserviceBase):
    def __init__(self):
        super().__init__("service_name")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and sites based on the given site names.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/historic_data.json not found")
            return []  # or empty dict based on data structure
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return []  # or empty dict based on data structure

    @staticmethod
    def validate_input(site_names: List[str]):
        for site_name in site_names:
            if site_name not in ServiceName.data:
                raise HTTPException(status_code=404, detail=f"{site_name} not found")

    @staticmethod
    def process_request(site_names: List[str]) -> List[HistoricData]:
        ServiceName.validate_input(site_names)
        return [ServiceName.data[site_name] for site_name in site_names]

    def register_routes(self):
        @self.app.post("/historic_data")
        async def get_historic_data(site_names: List[str]):
            return {
               'site_names': site_names,
                'historic_data': ServiceName.process_request(site_names)
            }

def start_service_name():
    service = ServiceName()
    service.run()

if __name__ == "__main__":
    start_service_name()
