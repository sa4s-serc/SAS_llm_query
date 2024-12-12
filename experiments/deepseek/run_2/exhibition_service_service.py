import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class ExhibitionRequest(BaseModel):
    interested_audience: Optional[List[str]] = None
    location: Optional[str] = None
    date_range: Optional[str] = None
    exhibition_type: Optional[str] = None

class ExhibitionService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_service")
        self.update_service_info(
            description="Service to track museum and art exhibitions by filtering based on audience type, venue location, exhibition dates, and category.",
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
        @self.app.post("/filter-exhibitions/")
        def filter_exhibitions(request: ExhibitionRequest):
            return self.process_request(request)

    def process_request(self, request: ExhibitionRequest):
        filtered_data = self.data
        if request.interested_audience:
            filtered_data = [item for item in filtered_data if item['interested_audience'] in request.interested_audience]
        if request.location:
            filtered_data = [item for item in filtered_data if item['location'] == request.location]
        if request.date_range:
            filtered_data = [item for item in filtered_data if item['date_range'] == request.date_range]
        if request.exhibition_type:
            filtered_data = [item for item in filtered_data if item['exhibition_type'] == request.exhibition_type]
        return filtered_data

    def start_exhibition_service():
        service = ExhibitionService()
        service.run()

    if __name__ == "__main__":
        start_exhibition_service()
