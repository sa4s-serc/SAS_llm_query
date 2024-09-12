from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("EventsService")


class EventsService(MicroserviceBase):
    def __init__(self):
        super().__init__("events_service")

        self.update_service_info(
            description="Provides information on upcoming campus events",
            dependencies=[],
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for upcoming events data")
            return self._get_events()

    # Service-specific logic
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
        selected_events = random.sample(events, k=2)
        logger.info(f"Generated upcoming events data: {selected_events}")
        return {"upcoming_events": selected_events}


def start_events_service():
    service = EventsService()
    service.run()


if __name__ == "__main__":
    start_events_service()
