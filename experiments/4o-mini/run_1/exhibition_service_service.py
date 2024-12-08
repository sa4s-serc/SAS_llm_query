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
            description="Service for tracking and filtering exhibitions based on criteria",
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
        @self.app.post("/filter_exhibitions/")
        async def filter_exhibitions(interested_audience: Optional[List[str]] = None,
                                     location: Optional[List[str]] = None,
                                     date_range: Optional[List[str]] = None,
                                     exhibition_type: Optional[List[str]] = None):
            result = self.process_request(interested_audience, location, date_range, exhibition_type)
            return result

    def process_request(self, interested_audience, location, date_range, exhibition_type):
        filtered_exhibitions = []
        for exhibition in self.data:
            if (interested_audience and exhibition['interested_audience'] not in interested_audience) or 
               (location and exhibition['location'] not in location) or 
               (date_range and exhibition['date_range'] not in date_range) or 
               (exhibition_type and exhibition['exhibition_type'] not in exhibition_type):
                continue
            filtered_exhibitions.append(exhibition)
        return filtered_exhibitions

    def start_service_name():
        service = ExhibitionService()
        service.register_routes()
        service.run()


if __name__ == "__main__":
    start_service_name()
