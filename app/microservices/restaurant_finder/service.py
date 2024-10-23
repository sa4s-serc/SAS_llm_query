import json
from fastapi import HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
from app.microservices.base import MicroserviceBase

class RestaurantFinderParams(BaseModel):
    location: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[List[int]] = None
    dietary_restrictions: Optional[str] = None
    group_size: Optional[int] = None

class RestaurantFinderService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_finder_service")
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
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_restaurants = self.restaurant_data

        if params.get('location'):
            filtered_restaurants = [r for r in filtered_restaurants if r['location'] == params['location']]
        if params.get('cuisine_type'):
            filtered_restaurants = [r for r in filtered_restaurants if r['cuisine_type'] == params['cuisine_type']]
        if params.get('price_range'):
            min_price, max_price = params['price_range']
            filtered_restaurants = [r for r in filtered_restaurants if min_price <= r['price_range(per person)'] <= max_price]
        if params.get('dietary_restrictions'):
            filtered_restaurants = [r for r in filtered_restaurants if r['dietary_restrictions'] == params['dietary_restrictions']]
        if params.get('group_size'):
            filtered_restaurants = [r for r in filtered_restaurants if r['group_size'] >= params['group_size']]

        self.logger.info(f"Filtered restaurants: {filtered_restaurants}")
        return {"restaurants": filtered_restaurants}

def start_restaurant_finder_service():
    service = RestaurantFinderService()
    service.run()

if __name__ == "__main__":
    start_restaurant_finder_service()
