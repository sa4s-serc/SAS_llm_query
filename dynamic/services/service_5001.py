from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional, List
import json
import logging

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MicroserviceBase:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.app = FastAPI()

    def update_service_info(self, description: str, dependencies: list):
        self.description = description
        self.dependencies = dependencies

class RestaurantRecommendationService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation")
        self.update_service_info(
            description="Service to recommend restaurants based on user preferences.",
            dependencies=[]
        )
        self.data = self.load_data()
        self.register_routes()

    def load_data(self):
        try:
            with open('data/specific_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("specific_data.json not found")
            return []
        except json.JSONDecodeError:
            logger.error("Error decoding specific_data.json")
            return []

    def register_routes(self):
        @self.app.post("/recommend_restaurants")
        async def recommend_restaurants(params: RestaurantParams):
            logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        logger.info(f"Processing request with params: {params}")
        filtered_data = self.data

        # Filter by location
        if params.get('location'):
            filtered_data = [d for d in filtered_data if d['location'] == params['location']]
            logger.info(f"After location filter: {len(filtered_data)} items")

        # Filter by cuisine type
        if params.get('cuisine_type'):
            cuisine_types = params['cuisine_type']
            if isinstance(cuisine_types, str):
                cuisine_types = [cuisine_types]
            filtered_data = [d for d in filtered_data if d['cuisine_type'] in cuisine_types]
            logger.info(f"After cuisine type filter: {len(filtered_data)} items")

        # Filter by price range
        if params.get('price_range'):
            price_range = params['price_range']
            filtered_data = [d for d in filtered_data if d['price_range'] in price_range]
            logger.info(f"After price range filter: {len(filtered_data)} items")

        # Filter by dietary restrictions
        if params.get('dietary_restrictions'):
            dietary_restrictions = params['dietary_restrictions']
            filtered_data = [d for d in filtered_data if not set(dietary_restrictions).intersection(d['dietary_restrictions'])]
            logger.info(f"After dietary restrictions filter: {len(filtered_data)} items")

        # Filter by group size
        if params.get('group_size'):
            filtered_data = [d for d in filtered_data if d['capacity'] >= params['group_size']]
            logger.info(f"After group size filter: {len(filtered_data)} items")

        if not filtered_data:
            return {"items": [], "message": "No items found matching criteria"}

        return {"items": filtered_data, "message": f"Found {len(filtered_data)} matching items"}

class RestaurantParams(BaseModel):
    location: Optional[str] = Field(None, description="The location to filter restaurants by.")
    cuisine_type: Optional[List[str]] = Field(None, description="List of preferred cuisine types.")
    price_range: Optional[List[str]] = Field(None, description="List of acceptable price ranges.")
    dietary_restrictions: Optional[List[str]] = Field(None, description="List of dietary restrictions.")
    group_size: Optional[int] = Field(None, description="Size of the group for dining.")

# To run the application, use the command: uvicorn filename:app --host 0.0.0.0 --port 5001
