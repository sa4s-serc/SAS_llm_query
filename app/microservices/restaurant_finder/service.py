import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from app.microservices.base import MicroserviceBase

class RestaurantFinderParams(BaseModel):
    user_location: str
    cuisine_type: str
    price_range: Tuple[int, int]
    dietary_restrictions: str
    group_size: int

class RestaurantFinderService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_finder")
        self.update_service_info(
            description="Recommends restaurants based on cuisine preferences and location",
            dependencies=[]
        )
        self.restaurant_data = self.load_restaurant_data()

    def load_restaurant_data(self):
        with open('data/restaurant_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/restaurant_finder")
        async def find_restaurants(params: RestaurantFinderParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        # Simple filtering based on parameters
        filtered_restaurants = [
            restaurant for restaurant in self.restaurant_data
            if (restaurant['cuisine_type'] == params['cuisine_type'] and
                params['price_range'][0] <= restaurant['price_range(per person)'] <= params['price_range'][1] and
                restaurant['dietary_restrictions'] == params['dietary_restrictions'] and
                restaurant['group_size'] >= params['group_size'])
        ]
        return {"restaurants": filtered_restaurants}

def start_restaurant_finder_service():
    service = RestaurantFinderService()
    service.run()

if __name__ == "__main__":
    start_restaurant_finder_service()
