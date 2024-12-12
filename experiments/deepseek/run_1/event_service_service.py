import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class EventRequest(BaseModel):
    category: Optional[str] = None
    time_commitment: Optional[str] = None

class EventService(MicroserviceBase):
    def __init__(self):
        super().__init__("event_service")
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
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/event_notifier.json")
            return []

    def register_routes(self):
        @self.app.post("/events/")
        async def get_events(request: EventRequest):
            return self.process_request(request)

    def process_request(self, request: EventRequest):
        filtered_events = self.data
        if request.category:
            filtered_events = [event for event in filtered_events if request.category.lower() in event['event'].lower()]
        if request.time_commitment:
            filtered_events = [event for event in filtered_events if request.time_commitment.lower() == event['time_required'].lower()]
        return filtered_events

def start_event_service():
    service = EventService()
    service.run()

if __name__ == "__main__":
    start_event_service()
