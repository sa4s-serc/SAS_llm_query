import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class SiteRequest(BaseModel):
    site_names: List[str]

class HistoricDataService(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_data_service")
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
            return {}
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return {}

    def register_routes(self):
        @self.app.post("/historic-data/")
        async def get_historic_data(request: SiteRequest):
            return self.process_request(request)

    def process_request(self, request: SiteRequest):
        results = []
        for site_name in request.site_names:
            if site_name in self.data:
                results.append(self.data[site_name])
            else:
                raise HTTPException(status_code=404, detail=f"Site '{site_name}' not found.")
        return results

def start_historic_data_service():
    service = HistoricDataService()
    service.run()

if __name__ == "__main__":
    start_historic_data_service()
