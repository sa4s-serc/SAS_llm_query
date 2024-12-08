import json
from fastapi import FastAPI, HTTPException
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
            description="Service to track museum and art exhibitions based on audience type, venue location, exhibition dates, and category.",
            dependencies=[]
        )
        self.data = self.load_data()
        
        self.register_routes()

    def load_data(self):
        try:
            with open('data/exhibition_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/exhibition_data.json not found")
            return []  # or empty dict based on data structure
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/exhibition_data.json")
            return []  # or empty dict based on data structure

    def register_routes(self):
        @self.app.post("/exhibitions")
        async def get_exhibitions(interested_audience: Optional[List[str]] = None,
                                  location: Optional[str] = None,
                                  date_range: Optional[str] = None,
                                  exhibition_type: Optional[List[str]] = None):
            return self.process_request(interested_audience, location, date_range, exhibition_type)

    def process_request(self, interested_audience, location, date_range, exhibition_type):
        filtered_exhibitions = []
        for exhibition in self.data:
            if (   (not interested_audience or exhibition['interested_audience'] in interested_audience)
                and (not location or exhibition['location'] == location)
                and (not date_range or exhibition['date_range'] == date_range)
                and (not exhibition_type or exhibition['exhibition_type'] in exhibition_type)):
                filtered_exhibitions.append(exhibition)
        return filtered_exhibitions


def start_exhibition_service():
    service = ExhibitionService()
    service.run()


if __name__ == "__main__":
    start_exhibition_service()
