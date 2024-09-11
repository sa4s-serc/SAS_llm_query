from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class CampusEventsService(MicroserviceBase):
    def __init__(self):
        super().__init__("CampusEvents", microservice_ports['event_campus_events'])

        @self.app.get("/data")
        async def get_data():
            return self._get_campus_events()

    def _get_campus_events(self):
        events = [
            "Tech Talk at 4 PM in Lecture Hall",
            "Music Festival this weekend",
            "Career Fair next Tuesday",
            "Sports Day on Saturday",
            "Art Exhibition in the Student Center"
        ]
        return {"upcoming_events": random.sample(events, 2)}

def start_campus_events_service():
    service = CampusEventsService()
    service.start()

if __name__ == "__main__":
    start_campus_events_service()
