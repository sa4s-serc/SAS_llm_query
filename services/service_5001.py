import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class Restaurant(BaseModel):
    location: Optional[str]
    cuisine_type: Optional[str]
    price_range: Optional[str]
    dietary_restrictions: Optional[List[str]]
    group_size: Optional[int]


class ServiceName(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation_service")
        self.update_service_info(
            description="A service to recommend restaurants based on user preferences.",
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

    def recommend_restaurants(self, preferences: Restaurant):
        matched_restaurants = []
        for restaurant in self.data:
            if self.match_preferences(restaurant, preferences):
                matched_restaurants.append(restaurant)
        return matched_restaurants

    def match_preferences(self, restaurant, preferences):
        if preferences.location and preferences.location.lower() not in restaurant['location'].lower():
            return False
        if preferences.cuisine_type and preferences.cuisine_type.lower() != restaurant['cuisine_type'].lower():
            return False
        if preferences.price_range and preferences.price_range.lower() != restaurant['price_range'].lower():
            return False
        if preferences.dietary_restrictions:
            if not all(item in restaurant['dietary_restrictions'] for item in preferences.dietary_restrictions):
                return False
        if preferences.group_size and preferences.group_size > restaurant['group_size']:
            return False
        return True

app = FastAPI()

service = ServiceName()

@app.post("/recommend")
async def recommend(preferences: Restaurant):
    recommendations = service.recommend_restaurants(preferences.dict())
    if not recommendations:
        raise HTTPException(status_code=404, detail="No restaurants found matching preferences")
    return recommendations


def start_service_name():
    service = ServiceName()
    service.run()

if __name__ == "__main__":
    start_service_name()
