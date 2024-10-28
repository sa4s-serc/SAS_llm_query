import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.microservices.base import MicroserviceBase

class Event(BaseModel):
    event: str
    time_required: str
    details: str

class EventNotifierParams(BaseModel):
    event_type: Optional[List[str]] = None
    duration: Optional[List[str]] = None

class EventNotifierService(MicroserviceBase):
    def __init__(self):
        super().__init__("event_notifier")
        self.update_service_info(
            description="Sends notifications about upcoming events, shows, and festivals",
            dependencies=[]
        )
        self.events = self.load_events()

    def load_events(self):
        try:
            with open('data/event_notifier.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("event_notifier.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding event_notifier.json")
            return []

    def register_routes(self):
        @self.app.post("/event_notifier")
        async def get_events(params: EventNotifierParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_events = self.events

        if params.get('event_type'):
            event_types = params['event_type']
            if isinstance(event_types, str):
                event_types = [event_types]
            filtered_events = [e for e in filtered_events 
                             if any(t.lower() in e['event'].lower() for t in event_types)]
            self.logger.info(f"After event type filter: {len(filtered_events)} events")

        if params.get('duration'):
            durations = params['duration']
            if isinstance(durations, str):
                durations = [durations]
            filtered_events = [e for e in filtered_events 
                             if any(d in e['time_required'] for d in durations)]
            self.logger.info(f"After duration filter: {len(filtered_events)} events")

        if not filtered_events:
            self.logger.warning("No events found matching the criteria")
            return {
                "events": [],
                "message": "No events found matching your criteria."
            }

        self.logger.info(f"Returning {len(filtered_events)} events")
        return {
            "events": filtered_events,
            "message": f"Found {len(filtered_events)} events matching your criteria."
        }

def start_event_notifier_service():
    service = EventNotifierService()
    service.run()

if __name__ == "__main__":
    start_event_notifier_service()
