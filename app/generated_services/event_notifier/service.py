import json
from fastapi import HTTPException, FastAPI
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class Event(BaseModel):
    event: str
    time_required: str
    details: str


class CityEvents(MicroserviceBase):
    def __init__(self):
        super().__init__("city_events")  # service_name without _service suffix
        self.update_service_info(
            description="Provides information about city events, festivals, and shows based on category and time commitment.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/event_notifier.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/event_notifier.json not found")
            return []  # or empty dict based on data structure
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/event_notifier.json")
            return []  # or empty dict based on data structure

    def register_routes(self):
        @self.app.post("/events/", response_model=List[Event])
        async def get_events(category: Optional[str] = None, time_commitment: Optional[str] = None):
            return self.process_request(category, time_commitment)

    def process_request(self, category: Optional[str], time_commitment: Optional[str]):
        filtered_events = []
        for event in self.data:
            if (category is None or category in event.get('event', '').lower()) and \
               (time_commitment is None or time_commitment in event.get('time_required', '').lower()):
                filtered_events.append(event)
        return filtered_events


def start_city_events():
    service = CityEvents()
    service.register_routes()
    service.run()


if __name__ == "__main__":
    start_city_events()
