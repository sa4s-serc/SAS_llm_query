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
        super().__init__("travel")
        self.update_service_info(
            description="Provides travel options based on destination, available time, and preferred mode of transport.",
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
        @self.app.post('/travel-options/', response_model=List[TravelOption])
        async def get_travel_options(destination: Optional[str] = None, available_time: Optional[int] = None, preferred_mode: Optional[str] = None):
            options = self.process_request(destination, available_time, preferred_mode)
            if not options:
                raise HTTPException(status_code=404, detail="No travel options found")
            return options

    def process_request(self, destination: Optional[str], available_time: Optional[int], preferred_mode: Optional[str]) -> List[dict]:
        filtered_options = []
        for option in self.data:
            if (destination and option['destination'] != destination) or \
               (available_time and option['available_time'] > available_time) or \
               (preferred_mode and option['preferred_mode'] != preferred_mode):
                continue
            filtered_options.append(option)
        return filtered_options

def start_travel():
    service = TravelService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_travel()
