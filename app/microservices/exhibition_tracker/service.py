import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from app.microservices.base import MicroserviceBase

class ExhibitionTrackerParams(BaseModel):
    user_interests: List[str]
    user_location: str
    date_range: str
    exhibition_type: str

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
        # Simple filtering based on parameters
        filtered_exhibitions = [
            exhibition for exhibition in self.exhibition_data
            if (exhibition['exhibition_type'] == params['exhibition_type'] and
                exhibition['interested_audience'] in params['user_interests'] and
                self.is_in_date_range(exhibition['date_range'], params['date_range']))
        ]
        return {"exhibitions": filtered_exhibitions}

    def is_in_date_range(self, exhibition_range, user_range):
        # Simple date range check (assuming format "YYYY-MM-DD - YYYY-MM-DD")
        exhibition_start, exhibition_end = exhibition_range.split(' - ')
        user_start, user_end = user_range.split(',')
        return exhibition_start <= user_end and exhibition_end >= user_start

def start_exhibition_tracker_service():
    service = ExhibitionTrackerService()
    service.run()

if __name__ == "__main__":
    start_exhibition_tracker_service()
