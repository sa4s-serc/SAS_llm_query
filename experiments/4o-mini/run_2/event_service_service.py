import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class Event(BaseModel):
    event: str
    time_required: str
    details: str


class EventService(MicroserviceBase):
    def __init__(self):
        super().__init__("event_service")
        self.update_service_info(
            description="Service providing information about city events, festivals, and shows based on category and time commitment",
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
        @self.app.post("/events/")
        async def get_events(category: Optional[List[str]] = None, time_commitment: Optional[str] = None):
            return self.process_request(category, time_commitment)

    def process_request(self, category: Optional[List[str]], time_commitment: Optional[str]):
        filtered_events = []
        for event in self.data:
            if (category is None or event.get('category') in category) and \
               (time_commitment is None or event.get('time_required') == time_commitment):
                filtered_events.append(event)
        return filtered_events


def start_event_service():
    service = EventService()
    service.run()

if __name__ == '__main__':
    start_event_service()
