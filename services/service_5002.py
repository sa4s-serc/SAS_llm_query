import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class HistoricSite(BaseModel):
    name: Optional[str]
    year_built: Optional[str]
    significance: Optional[str]
    cultural_importance: Optional[str]
    location: Optional[str]
    description: Optional[str]

class HistoricDataService(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_data_service")
        self.update_service_info(
            description="Service to provide historical details of monuments and historical sites",
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

    def get_historic_sites(self, site_names: Optional[List[str]]):
        if not site_names:
            raise HTTPException(status_code=400, detail="No site names provided")
        results = []
        for name in site_names:
            site_info = self.data.get(name)
            if site_info:
                results.append(HistoricSite(**site_info))
            else:
                raise HTTPException(status_code=404, detail=f"Site '{name}' not found")
        return results

app = FastAPI()

service = HistoricDataService()

@app.get("/historic_sites", response_model=List[HistoricSite])
async def read_historic_sites(site_names: Optional[List[str]] = None):
    return service.get_historic_sites(site_names)


def start_service_name():
    service = HistoricDataService()
    service.run()

if __name__ == "__main__":
    start_service_name()
