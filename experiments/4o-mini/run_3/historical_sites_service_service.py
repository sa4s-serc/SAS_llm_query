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
            description="Service to provide historical and cultural details about monuments and sites",
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
        @self.app.post("/historical_sites/", response_model=List[HistoricData])
        async def get_historical_sites(site_names: Optional[List[str]]):
            result = self.process_request(site_names)
            if not result:
                raise HTTPException(status_code=404, detail="Sites not found")
            return result

    def process_request(self, site_names: Optional[List[str]]):
        results = []
        for name in site_names:
            site_info = self.data.get(name)
            if site_info:
                results.append(HistoricData(**site_info))
        return results

def start_historical_sites_service():
    service = HistoricalSitesService()
    service.run()

if __name__ == '__main__':
    start_historical_sites_service()
