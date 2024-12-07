import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class TravelOption(BaseModel):
    destination: str
    available_time: int
    preferred_mode: str

class TravelService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_service")
        self.update_service_info(
            description="Service to provide travel options based on criteria",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/travel.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/travel.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/travel.json")
            return []

    def register_routes(self):
        @self.app.post("/travel-options/")
        async def get_travel_options(destination: Optional[str] = None, available_time: Optional[int] = None, preferred_mode: Optional[List[str]] = None):
            return self.process_request(destination, available_time, preferred_mode)

    def process_request(self, destination, available_time, preferred_mode):
        filtered_options = [option for option in self.data if 
            (destination is None or option['destination'] == destination) and 
            (available_time is None or option['available_time'] <= available_time) and 
            (preferred_mode is None or option['preferred_mode'] in preferred_mode)]
        if not filtered_options:
            raise HTTPException(status_code=404, detail="No travel options found")
        return filtered_options

def start_travel_service():
    service = TravelService()
    service.run()

if __name__ == "__main__":
    start_travel_service()
