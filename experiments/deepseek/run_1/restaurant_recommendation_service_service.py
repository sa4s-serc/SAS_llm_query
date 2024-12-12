import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class RestaurantRecommendationRequest(BaseModel):
    location: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    group_size: Optional[int] = None

class RestaurantRecommendationService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation_service")
        self.update_service_info(
            description="Service to recommend restaurants based on user preferences.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/restaurant_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/restaurant_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/restaurant_data.json")
            return []

    def register_routes(self):
        @self.app.post("/recommend")
        async def recommend_restaurants(request: RestaurantRecommendationRequest):
            return self.process_request(request)

    def process_request(self, request: RestaurantRecommendationRequest):
        filtered_restaurants = self.data
        if request.location:
            filtered_restaurants = [r for r in filtered_restaurants if r['location'] == request.location]
        if request.cuisine_type:
            filtered_restaurants = [r for r in filtered_restaurants if r['cuisine_type'] == request.cuisine_type]
        if request.price_range:
            filtered_restaurants = [r for r in filtered_restaurants if r['price_range'] == request.price_range]
        if request.dietary_restrictions:
            filtered_restaurants = [r for r in filtered_restaurants if all(dr in r['dietary_restrictions'] for dr in request.dietary_restrictions)]
        if request.group_size:
            filtered_restaurants = [r for r in filtered_restaurants if r['group_size'] >= request.group_size]
        return filtered_restaurants


def start_restaurant_recommendation_service():
    service = RestaurantRecommendationService()
    service.run()

if __name__ == "__main__":
    start_restaurant_recommendation_service()
