import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase

class TravelOptionsParams(BaseModel):
    destination: str
    available_time: Optional[int] = None
    preferred_mode: Optional[str] = None

class TravelOptionsService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_options")
        self.update_service_info(
            description="Provides transportation options and routes to tourist destinations",
            dependencies=[]
        )
        self.travel_options = self.load_travel_options()

    def load_travel_options(self):
        with open('data/travel.txt', 'r') as f:
            return [eval(line) for line in f]

    def register_routes(self):
        @self.app.post("/travel_options")
        async def get_travel_options(params: TravelOptionsParams):
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_options = self.travel_options

        if params.get('destination'):
            filtered_options = [opt for opt in filtered_options if opt['destination'] == params['destination']]
        if params.get('available_time'):
            filtered_options = [opt for opt in filtered_options if opt['available_time'] <= params['available_time']]
        if params.get('preferred_mode'):
            filtered_options = [opt for opt in filtered_options if opt['preferred_mode'] == params['preferred_mode']]

        self.logger.info(f"Filtered travel options: {filtered_options}")
        return {"travel_options": filtered_options}

def start_travel_options_service():
    service = TravelOptionsService()
    service.run()

if __name__ == "__main__":
    start_travel_options_service()
