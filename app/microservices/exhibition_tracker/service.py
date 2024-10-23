import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase
from datetime import datetime

class ExhibitionTrackerParams(BaseModel):
    interested_audience: Optional[str] = None
    location: Optional[str] = None
    date_range: Optional[str] = None
    exhibition_type: Optional[str] = None

class ExhibitionTrackerService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibition_tracker")
        self.update_service_info(
            description="Tracks and notifies users about ongoing and upcoming exhibitions",
            dependencies=[]
        )
        self.exhibition_data = self.load_exhibition_data()

    def load_exhibition_data(self):
        with open('data/exhibition_data.json', 'r') as f:
            return json.load(f)

    def register_routes(self):
        @self.app.post("/exhibition_tracker")
        async def track_exhibitions(params: ExhibitionTrackerParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        filtered_exhibitions = self.exhibition_data

        if params.get('interested_audience'):
            filtered_exhibitions = [e for e in filtered_exhibitions if e['interested_audience'] == params['interested_audience']]
        if params.get('location'):
            filtered_exhibitions = [e for e in filtered_exhibitions if e['location'] == params['location']]
        if params.get('date_range'):
            start, end = params['date_range'].split(',')
            filtered_exhibitions = [e for e in filtered_exhibitions if self.is_date_in_range(e['date_range'], start, end)]
        if params.get('exhibition_type'):
            filtered_exhibitions = [e for e in filtered_exhibitions if e['exhibition_type'] == params['exhibition_type']]

        return {"exhibitions": filtered_exhibitions}

    def is_date_in_range(self, exhibition_range, start, end):
        exhibition_start, exhibition_end = exhibition_range.split(' - ')
        return exhibition_start <= end and exhibition_end >= start

def start_exhibition_tracker_service():
    service = ExhibitionTrackerService()
    service.run()

if __name__ == "__main__":
    start_exhibition_tracker_service()
