import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class Exhibition(BaseModel):
    interested_audience: str
    location: str
    date_range: str
    exhibition_type: str


class ExhibitionService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_service")
        self.update_service_info(
            description="Service to track museum and art exhibitions based on audience type, venue location, exhibition dates, and category.",
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
        @self.app.post("/exhibitions/")
        async def filter_exhibitions(interested_audience: Optional[List[str]] = None, location: Optional[str] = None, date_range: Optional[str] = None, exhibition_type: Optional[str] = None):
            try:
                return self.process_request(interested_audience, location, date_range, exhibition_type)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

    def process_request(self, interested_audience, location, date_range, exhibition_type):
        filtered_exhibitions = []
        for exhibition in self.data:
            if ((interested_audience is None or exhibition['interested_audience'] in interested_audience) and
                (location is None or exhibition['location'] == location) and
                (date_range is None or exhibition['date_range'] == date_range) and
                (exhibition_type is None or exhibition['exhibition_type'] == exhibition_type)):
                filtered_exhibitions.append(exhibition)
        return filtered_exhibitions


def start_exhibition_service():
    service = ExhibitionService()
    service.run()

if __name__ == "__main__":
    start_exhibition_service()
