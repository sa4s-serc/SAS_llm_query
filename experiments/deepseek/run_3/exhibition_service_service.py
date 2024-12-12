import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class ExhibitionFilter(BaseModel):
    interested_audience: Optional[List[str]] = None
    location: Optional[str] = None
    date_range: Optional[str] = None
    exhibition_type: Optional[List[str]] = None

class ExhibitionService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_service")
        self.update_service_info(
            description="Service to filter and retrieve museum and art exhibitions based on audience type, venue location, exhibition dates, and category.",
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
        async def filter_exhibitions(filters: ExhibitionFilter):
            return self.process_request(filters)

    def process_request(self, filters: ExhibitionFilter):
        filtered_data = self.data
        if filters.interested_audience:
            filtered_data = [item for item in filtered_data if item['interested_audience'] in filters.interested_audience]
        if filters.location:
            filtered_data = [item for item in filtered_data if item['location'] == filters.location]
        if filters.date_range:
            filtered_data = [item for item in filtered_data if item['date_range'] == filters.date_range]
        if filters.exhibition_type:
            filtered_data = [item for item in filtered_data if item['exhibition_type'] in filters.exhibition_type]
        return filtered_data

    def start_exhibition_service():
        service = ExhibitionService()
        service.run()

    if __name__ == "__main__":
        start_exhibition_service()
