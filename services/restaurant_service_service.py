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

class RestaurantService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_service")
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

    def process_request(self, location: str, cuisine_type: str, price_range: str, dietary_restrictions: Optional[List[str]], group_size: int):
        results = []
        for restaurant in self.data:
            if (restaurant['location'] == location and
                restaurant['cuisine_type'] == cuisine_type and
                restaurant['price_range'] == price_range and
                (not dietary_restrictions or all(dr in restaurant['dietary_restrictions'] for dr in dietary_restrictions)) and
                restaurant['group_size'] >= group_size):
                results.append(restaurant)
        return results

    def register_routes(self):
        @self.app.post("/recommend_restaurants")
        async def recommend_restaurants(location: str, cuisine_type: str, price_range: str, dietary_restrictions: Optional[List[str]] = None, group_size: int = 1):
            recommendations = self.process_request(location, cuisine_type, price_range, dietary_restrictions, group_size)
            if not recommendations:
                raise HTTPException(status_code=404, detail="No matching restaurants found")
            return recommendations

def start_service_name():
    service = RestaurantService()
    service.run()

if __name__ == "__main__":
    start_service_name()
