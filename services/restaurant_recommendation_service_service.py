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

    def process_request(self, location: Optional[str], cuisine_type: Optional[str], price_range: Optional[str], dietary_restrictions: Optional[List[str]], group_size: Optional[int]):
        recommendations = []
        for restaurant in self.data:
            if ( (location is None or restaurant['location'] == location) and
                 (cuisine_type is None or restaurant['cuisine_type'] == cuisine_type) and
                 (price_range is None or restaurant['price_range'] == price_range) and
                 (dietary_restrictions is None or all(dr in restaurant['dietary_restrictions'] for dr in dietary_restrictions)) and
                 (group_size is None or restaurant['group_size'] >= group_size) ):  
                recommendations.append(restaurant)
        return recommendations

    def register_routes(self, app: FastAPI):
        @app.post("/recommend/restaurants")
        async def recommend_restaurants(location: Optional[str] = None, cuisine_type: Optional[str] = None, price_range: Optional[str] = None, dietary_restrictions: Optional[List[str]] = None, group_size: Optional[int] = None):
            try:
                results = self.process_request(location, cuisine_type, price_range, dietary_restrictions, group_size)
                return results
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))


def start_service_name():
    service = RestaurantRecommendationService()
    service.run()

if __name__ == "__main__":
    start_service_name()
