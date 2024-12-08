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
        super().__init__("restaurant_recommendation")
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
        @self.app.post("/recommendations/")
        async def recommend_restaurants(preferences: Restaurant):
            recommendations = self.process_request(preferences)
            return recommendations

    def process_request(self, preferences: Restaurant):
        filtered_restaurants = []
        for restaurant in self.data:
            if (restaurant['location'] == preferences.location and 
                restaurant['cuisine_type'] == preferences.cuisine_type and 
                restaurant['price_range'] == preferences.price_range and 
                (not preferences.dietary_restrictions or 
                 set(preferences.dietary_restrictions).issubset(set(restaurant['dietary_restrictions']))) and 
                restaurant['group_size'] >= preferences.group_size):
                filtered_restaurants.append(restaurant)
        return filtered_restaurants

def start_restaurant_recommendation():
    service = RestaurantRecommendationService()
    service.run()

if __name__ == "__main__":
    start_restaurant_recommendation()
