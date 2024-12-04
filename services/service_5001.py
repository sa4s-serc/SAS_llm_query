from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
import json

class MicroserviceBase:
    def __init__(self, service_name):
        self.service_name = service_name
        self.app = FastAPI()
        self.logger = self.setup_logger()  # Assume a logging setup method

    def setup_logger(self):
        # Placeholder for logger setup
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(self.service_name)

    def update_service_info(self, description, dependencies):
        self.description = description
        self.dependencies = dependencies

class RestaurantRecommendationService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation_service")
        self.update_service_info(
            description="A service to recommend restaurants based on user preferences.",
            dependencies=[]
        )
        self.data = self.load_data()
        self.register_routes()

    def load_data(self):
        try:
            with open('data/specific_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/specific_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/specific_data.json")
            return []

    def register_routes(self):
        @self.app.post("/recommend")
        async def recommend(params: RestaurantRecommendationParams):
            self.logger.info("Processing request with params: " + str(params))
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info("Processing request with params: " + str(params))
        filtered_data = self.data

        # Filter by location
        if params.location:
            filtered_data = [d for d in filtered_data if d['location'] in params.location]
            self.logger.info("After location filter: " + str(len(filtered_data)) + " items")

        # Filter by cuisine type
        if params.cuisine:
            filtered_data = [d for d in filtered_data if d['cuisine'] in params.cuisine]
            self.logger.info("After cuisine filter: " + str(len(filtered_data)) + " items")

        # Filter by price range
        if params.price_range:
            filtered_data = [d for d in filtered_data if d['price_range'] in params.price_range]
            self.logger.info("After price range filter: " + str(len(filtered_data)) + " items")

        # Filter by dietary restrictions
        if params.dietary_restrictions:
            filtered_data = [d for d in filtered_data if not set(d['dietary_restrictions']).intersection(params.dietary_restrictions)]
            self.logger.info("After dietary restrictions filter: " + str(len(filtered_data)) + " items")

        # Filter by group size
        if params.group_size:
            filtered_data = [d for d in filtered_data if d['capacity'] >= params.group_size]
            self.logger.info("After group size filter: " + str(len(filtered_data)) + " items")

        if not filtered_data:
            return {"items": [], "message": "No items found matching criteria"}
        return {"items": filtered_data, "message": "Found " + str(len(filtered_data)) + " matching items"}

class RestaurantRecommendationParams(BaseModel):
    location: Optional[List[str]] = Field(default=None, description="List of preferred locations.")
    cuisine: Optional[List[str]] = Field(default=None, description="List of preferred cuisine types.")
    price_range: Optional[List[str]] = Field(default=None, description="List of acceptable price ranges.")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="List of dietary restrictions.")
    group_size: Optional[int] = Field(default=None, description="Preferred group size.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(RestaurantRecommendationService().app, host="0.0.0.0", port=5001)
