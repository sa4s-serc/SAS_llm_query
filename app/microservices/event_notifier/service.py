import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import List
from app.microservices.base import MicroserviceBase

class Event(BaseModel):
    event: str
    time_required: str
    details: str

class EventNotifierService(MicroserviceBase):
    def __init__(self):
        super().__init__("event_notifier")
        self.update_service_info(
            description="Sends notifications about upcoming events, shows, and festivals",
            dependencies=[]
        )
        self.events = self.load_events()

    def load_events(self):
        with open('data/event_notifier.json', 'r') as f:
            return [Event(**event) for event in json.load(f)]

    def register_routes(self):
        @self.app.get("/events", response_model=List[Event])
        async def get_events():
            return await self.process_request({})

    async def process_request(self, params):
        return self.events

def start_event_notifier_service():
    service = EventNotifierService()
    service.run()

if __name__ == "__main__":
    start_event_notifier_service()
