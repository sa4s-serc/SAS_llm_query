from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random


class EventsService(MicroserviceBase):
    def __init__(self):
        super().__init__("Events", microservice_ports["campus_events"])

        @self.app.get("/data")
        async def get_data():
            return self._get_events()

    def _get_events(self):
        events = [
            {"name": "Tech Fest", "date": "2024-09-15", "venue": "Main Auditorium"},
            {
                "name": "Cultural Night",
                "date": "2024-09-20",
                "venue": "Open Air Theatre",
            },
            {"name": "Career Fair", "date": "2024-09-25", "venue": "Convention Center"},
        ]
        return {"upcoming_events": random.sample(events, k=2)}


def start_events_service():
    service = EventsService()
    service.start()


if __name__ == "__main__":
    start_events_service()
