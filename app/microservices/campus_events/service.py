from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("CampusEventsService")


class CampusEventsService(MicroserviceBase):
    def __init__(self):
        super().__init__("campus_events_service")

        self.update_service_info(
            description="Provides information on upcoming campus events",
            dependencies=[],
        )

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for campus events data")
            return self._get_campus_events()

    # Service-specific logic
    def _get_campus_events(self):
        events = [
            "Tech Talk at 4 PM in Lecture Hall",
            "Music Festival this weekend",
            "Career Fair next Tuesday",
            "Sports Day on Saturday",
            "Art Exhibition in the Student Center",
        ]
        selected_events = random.sample(events, 2)
        logger.info(f"Generated campus events data: {selected_events}")
        return {"upcoming_events": selected_events}


def start_campus_events_service():
    service = CampusEventsService()
    service.run()


if __name__ == "__main__":
    start_campus_events_service()
