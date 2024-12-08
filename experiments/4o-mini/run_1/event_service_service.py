import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

# Pydantic model definition for event data
class Event(BaseModel):
    event: str
    time_required: str
    details: str

class EventService(MicroserviceBase):
    def __init__(self):
        super().__init__("event_service")
        self.update_service_info(
            description="Service to provide information about events based on type and duration filters",
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
        @app.post("/events/", response_model=List[Event])
        async def get_events(event_types: Optional[List[str]] = None, durations: Optional[List[str]] = None):
            filtered_events = self.process_request(event_types, durations)
            if not filtered_events:
                raise HTTPException(status_code=404, detail="No events found matching the criteria")
            return filtered_events

    def process_request(self, event_types: Optional[List[str]], durations: Optional[List[str]]):
        filtered_events = []
        for event in self.data:
            if (event_types is None or event['event'] in event_types) and (
                durations is None or event['time_required'] in durations
            ):
                filtered_events.append(Event(**event))
        return filtered_events

app = FastAPI()
service = EventService()
service.register_routes()

def start_event_service():
    service.run()

if __name__ == "__main__":
    start_event_service()
