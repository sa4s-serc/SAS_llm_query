import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class TravelOptionsParams(BaseModel):
    destination: Optional[List[str]] = None
    available_time: Optional[int] = None
    preferred_mode: Optional[List[str]] = None

class TravelOptionsService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_options")
        self.update_service_info(
            description="Provides transportation options and routes to tourist destinations",
            dependencies=[]
        )
        self.travel_options = self.load_travel_options()

    def load_travel_options(self):
        try:
            with open('data/travel.txt', 'r') as f:
                return [eval(line) for line in f]
        except FileNotFoundError:
            self.logger.error("travel.txt not found")
            return []
        except Exception as e:
            self.logger.error(f"Error loading travel options: {str(e)}")
            return []

    def register_routes(self):
        @self.app.post("/travel_options")
        async def get_travel_options(params: TravelOptionsParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_options = self.travel_options

        if params.get('destination'):
            destinations = params['destination']
            if isinstance(destinations, str):
                destinations = [destinations]
            filtered_options = [opt for opt in filtered_options 
                              if opt['destination'] in destinations]
            self.logger.info(f"After destination filter: {len(filtered_options)} options")

        if params.get('available_time'):
            filtered_options = [opt for opt in filtered_options 
                              if opt['available_time'] <= params['available_time']]
            self.logger.info(f"After time filter: {len(filtered_options)} options")

        if params.get('preferred_mode'):
            modes = params['preferred_mode']
            if isinstance(modes, str):
                modes = [modes]
            filtered_options = [opt for opt in filtered_options 
                              if opt['preferred_mode'] in modes]
            self.logger.info(f"After mode filter: {len(filtered_options)} options")

        if not filtered_options:
            self.logger.warning("No travel options found matching the criteria")
            return {
                "options": [],
                "message": "No travel options found matching your criteria."
            }

        self.logger.info(f"Returning {len(filtered_options)} travel options")
        return {
            "options": filtered_options,
            "message": f"Found {len(filtered_options)} travel options matching your criteria."
        }

def start_travel_options_service():
    service = TravelOptionsService()
    service.run()

if __name__ == "__main__":
    start_travel_options_service()
