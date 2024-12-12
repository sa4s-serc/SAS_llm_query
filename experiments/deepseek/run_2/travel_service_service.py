import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class TravelRequest(BaseModel):
    destination: Optional[str]
    available_time: Optional[int]
    preferred_mode: Optional[str]

class TravelService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_service")
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
        @self.app.post("/travel-options")
        async def get_travel_options(request: TravelRequest):
            return self.process_request(request)

    def process_request(self, request: TravelRequest):
        filtered_data = []
        for item in self.data:
            if (
                (not request.destination or item['destination'] == request.destination) and
                (not request.available_time or item['available_time'] <= request.available_time) and
                (not request.preferred_mode or item['preferred_mode'] == request.preferred_mode)
            ):
                filtered_data.append(item)
        return filtered_data

    def start_travel_service():
        service = TravelService()
        service.run()

    if __name__ == "__main__":
        start_travel_service()
