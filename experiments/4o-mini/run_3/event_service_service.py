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
            description="Service to provide information about city events, festivals, and shows.",
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

    def process_request(self, category: Optional[str] = None, time_commitment: Optional[str] = None):
        filtered_events = []
        for event in self.data:
            if (category is None or category in event['details']) and (
                time_commitment is None or time_commitment in event['time_required']
            ):
                filtered_events.append(event)
        return filtered_events

    def register_routes(self):
        @self.app.post("/events/", response_model=List[Event])
        async def get_events(category: Optional[str] = None, time_commitment: Optional[str] = None):
            events = self.process_request(category, time_commitment)
            if not events:
                raise HTTPException(status_code=404, detail="No events found matching criteria")
            return events


def start_event_service():
    service = EventService()
    service.run()


if __name__ == "__main__":
    start_event_service()
