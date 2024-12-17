import json
from fastapi import HTTPException, FastAPI
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class Exhibition(BaseModel):
    interested_audience: Optional[str]
    location: Optional[str]
    date_range: Optional[str]
    exhibition_type: Optional[str]

class ExhibitionService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_service")
        self.update_service_info(
            description="Service to track museum and art exhibitions based on various filters.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/exhibition_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/exhibition_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/exhibition_data.json")
            return []

    def register_routes(self):
        @self.app.post("/exhibitions", response_model=List[Exhibition])
        async def get_exhibitions(
            interested_audience: Optional[List[str]] = None,
            location: Optional[List[str]] = None,
            date_range: Optional[List[str]] = None,
            exhibition_type: Optional[List[str]] = None
        ):
            return self.process_request(interested_audience, location, date_range, exhibition_type)

    def process_request(self, interested_audience, location, date_range, exhibition_type):
        filtered_data = self.data
        if interested_audience:
            filtered_data = [exhibition for exhibition in filtered_data if exhibition['interested_audience'] in interested_audience]
        if location:
            filtered_data = [exhibition for exhibition in filtered_data if exhibition['location'] in location]
        if date_range:
            filtered_data = [exhibition for exhibition in filtered_data if exhibition['date_range'] in date_range]
        if exhibition_type:
            filtered_data = [exhibition for exhibition in filtered_data if exhibition['exhibition_type'] in exhibition_type]
        return filtered_data

def start_exhibition_service():
    service = ExhibitionService()
    service.register_routes()
    service.run()

if __name__ == "__main__":
    start_exhibition_service()
