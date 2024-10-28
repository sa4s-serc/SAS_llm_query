import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.microservices.base import MicroserviceBase

class RestaurantFinderParams(BaseModel):
    location: Optional[str] = None
    cuisine_type: Optional[List[str]] = None
    price_range: Optional[List[int]] = None
    dietary_restrictions: Optional[List[str]] = None
    group_size: Optional[List[int]] = None

class RestaurantFinderService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_finder")
        self.update_service_info(
            description="Recommends restaurants based on cuisine preferences and location",
            dependencies=[]
        )
        self.restaurant_data = self.load_restaurant_data()

    def load_restaurant_data(self):
        try:
            with open('data/restaurant_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("restaurant_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding restaurant_data.json")
            return []

    def register_routes(self):
        @self.app.post("/restaurant_finder")
        async def find_restaurants(params: RestaurantFinderParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_restaurants = self.restaurant_data

        if params.get('location'):
            filtered_restaurants = [r for r in filtered_restaurants 
                                 if r['location'] == params['location']]
            self.logger.info(f"After location filter: {len(filtered_restaurants)} restaurants")

        if params.get('cuisine_type'):
            # Handle list of cuisine types
            cuisine_types = params['cuisine_type']
            if isinstance(cuisine_types, str):
                cuisine_types = [cuisine_types]
            filtered_restaurants = [r for r in filtered_restaurants 
                                 if r['cuisine_type'] in cuisine_types]
            self.logger.info(f"After cuisine filter: {len(filtered_restaurants)} restaurants")

        if params.get('price_range'):
            # Handle list of price ranges
            price_ranges = params['price_range']
            if isinstance(price_ranges[0], str):
                price_ranges = [int(p) for p in price_ranges]
            filtered_restaurants = [r for r in filtered_restaurants 
                                 if r['price_range(per person)'] in price_ranges]
            self.logger.info(f"After price filter: {len(filtered_restaurants)} restaurants")

        if params.get('dietary_restrictions'):
            # Handle list of dietary restrictions
            restrictions = params['dietary_restrictions']
            if isinstance(restrictions, str):
                restrictions = [restrictions]
            filtered_restaurants = [r for r in filtered_restaurants 
                                 if r['dietary_restrictions'] in restrictions]
            self.logger.info(f"After dietary filter: {len(filtered_restaurants)} restaurants")

        if params.get('group_size'):
            # Handle list of group sizes
            group_sizes = params['group_size']
            if isinstance(group_sizes[0], str):
                group_sizes = [int(g) for g in group_sizes]
            filtered_restaurants = [r for r in filtered_restaurants 
                                 if r['group_size'] >= min(group_sizes)]
            self.logger.info(f"After group size filter: {len(filtered_restaurants)} restaurants")

        if not filtered_restaurants:
            self.logger.warning("No restaurants found matching the criteria")
            return {
                "restaurants": [],
                "message": "No restaurants found matching your criteria. Try adjusting your preferences."
            }

        self.logger.info(f"Returning {len(filtered_restaurants)} restaurants")
        return {
            "restaurants": filtered_restaurants,
            "message": f"Found {len(filtered_restaurants)} restaurants matching your criteria."
        }

def start_restaurant_finder_service():
    service = RestaurantFinderService()
    service.run()

if __name__ == "__main__":
    start_restaurant_finder_service()
