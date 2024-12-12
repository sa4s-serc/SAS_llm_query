import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase
from datetime import datetime

class ExhibitionTrackerParams(BaseModel):
    interested_audience: Optional[List[str]] = None
    location: Optional[List[str]] = None
    date_range: Optional[str] = None
    exhibition_type: Optional[List[str]] = None

class ExhibitionTrackerService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_tracker")
        self.update_service_info(
            description="Tracks and notifies users about ongoing and upcoming exhibitions",
            dependencies=[]
        )
        self.exhibition_data = self.load_exhibition_data()

    def load_exhibition_data(self):
        try:
            with open('data/exhibition_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("exhibition_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding exhibition_data.json")
            return []

    def register_routes(self):
        @self.app.post("/exhibition_tracker")
        async def track_exhibitions(params: ExhibitionTrackerParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_exhibitions = self.exhibition_data

        if params.get('interested_audience'):
            audiences = params['interested_audience']
            if isinstance(audiences, str):
                audiences = [audiences]
            filtered_exhibitions = [e for e in filtered_exhibitions 
                                 if e['interested_audience'] in audiences]
            self.logger.info(f"After audience filter: {len(filtered_exhibitions)} exhibitions")

        if params.get('location'):
            locations = params['location']
            if isinstance(locations, str):
                locations = [locations]
            filtered_exhibitions = [e for e in filtered_exhibitions 
                                 if e['location'] in locations]
            self.logger.info(f"After location filter: {len(filtered_exhibitions)} exhibitions")

        if params.get('date_range'):
            start, end = params['date_range'].split(',')
            filtered_exhibitions = [e for e in filtered_exhibitions 
                                 if self.is_date_in_range(e['date_range'], start, end)]
            self.logger.info(f"After date filter: {len(filtered_exhibitions)} exhibitions")

        if params.get('exhibition_type'):
            types = params['exhibition_type']
            if isinstance(types, str):
                types = [types]
            filtered_exhibitions = [e for e in filtered_exhibitions 
                                 if e['exhibition_type'] in types]
            self.logger.info(f"After type filter: {len(filtered_exhibitions)} exhibitions")

        if not filtered_exhibitions:
            self.logger.warning("No exhibitions found matching the criteria")
            return {
                "exhibitions": [],
                "message": "No exhibitions found matching your criteria."
            }

        self.logger.info(f"Returning {len(filtered_exhibitions)} exhibitions")
        return {
            "exhibitions": filtered_exhibitions,
            "message": f"Found {len(filtered_exhibitions)} exhibitions matching your criteria."
        }

    def is_date_in_range(self, exhibition_range: str, start: str, end: str) -> bool:
        try:
            exhibition_start, exhibition_end = exhibition_range.split(' - ')
            return exhibition_start <= end and exhibition_end >= start
        except Exception as e:
            self.logger.error(f"Error checking date range: {str(e)}")
            return False

def start_exhibition_tracker_service():
    service = ExhibitionTrackerService()
    service.run()

if __name__ == "__main__":
    start_exhibition_tracker_service()
