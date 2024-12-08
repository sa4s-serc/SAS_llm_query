import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class Restaurant(BaseModel):
    location: str
    cuisine_type: str
    price_range: str
    dietary_restrictions: Optional[List[str]]
    group_size: int


class RestaurantRecommendationService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation_service")
        self.update_service_info(
            description="Service to recommend restaurants based on user preferences",
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
        @self.app.post("/recommend/restaurants")
        async def recommend_restaurants(location: Optional[str] = None, cuisine_type: Optional[str] = None, price_range: Optional[str] = None, dietary_restrictions: Optional[List[str]] = None, group_size: Optional[int] = None):
            return self.process_request(location, cuisine_type, price_range, dietary_restrictions, group_size)

    def process_request(self, location, cuisine_type, price_range, dietary_restrictions, group_size):
        recommendations = []
        for restaurant in self.data:
            if (location and restaurant['location'] != location) or \
               (cuisine_type and restaurant['cuisine_type'] != cuisine_type) or \
               (price_range and restaurant['price_range'] != price_range) or \
               (dietary_restrictions and not set(dietary_restrictions).issubset(set(restaurant['dietary_restrictions']))) or \
               (group_size and restaurant['group_size'] < group_size):
                continue
            recommendations.append(restaurant)
        return recommendations


def start_service_name():
    service = RestaurantRecommendationService()
    service.register_routes()
    service.run()


if __name__ == '__main__':
    start_service_name()
