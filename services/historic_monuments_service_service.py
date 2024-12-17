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


class HistoricMonumentsService(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_monuments_service")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and historical sites",
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

    def process_request(self, site_names: List[str]):
        results = {}
        for name in site_names:
            site_info = self.data.get(name)
            if site_info is not None:
                results[name] = HistoricData(**site_info)
            else:
                raise HTTPException(status_code=404, detail=f"Site '{name}' not found")
        return results

    def register_routes(self):
        @self.app.post("/monuments")
        async def get_monuments(site_names: Optional[List[str]]):
            if not site_names:
                raise HTTPException(status_code=400, detail="Site names must be provided")
            return self.process_request(site_names)


def start_service_name():
    service = HistoricMonumentsService()
    service.run()

if __name__ == "__main__":
    start_service_name()
