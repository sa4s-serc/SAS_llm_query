from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("ClubsService")


class ClubsService(MicroserviceBase):
    def __init__(self):
        super().__init__("clubs_service")

        self.update_service_info(
            description="Provides information on club activities", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for club activities data")
            return self._get_club_activities()

    # Service-specific logic
    def _get_club_activities(self):
        activities = [
            "Coding Club: Hackathon next month",
            "Drama Club: Auditions this Friday",
            "Debate Club: Weekly meeting on Thursday",
            "Photography Club: Photo walk on Sunday",
            "Robotics Club: Robot building workshop",
        ]
        selected_activities = random.sample(activities, 2)
        logger.info(f"Generated club activities data: {selected_activities}")
        return {"club_activities": selected_activities}


def start_clubs_service():
    service = ClubsService()
    service.run()


if __name__ == "__main__":
    start_clubs_service()
