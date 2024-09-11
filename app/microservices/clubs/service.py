from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class ClubsService(MicroserviceBase):
    def __init__(self):
        super().__init__("Clubs", microservice_ports['event_clubs'])

        @self.app.get("/data")
        async def get_data():
            return self._get_club_activities()

    def _get_club_activities(self):
        activities = [
            "Coding Club: Hackathon next month",
            "Drama Club: Auditions this Friday",
            "Debate Club: Weekly meeting on Thursday",
            "Photography Club: Photo walk on Sunday",
            "Robotics Club: Robot building workshop"
        ]
        return {"club_activities": random.sample(activities, 2)}

def start_clubs_service():
    service = ClubsService()
    service.start()

if __name__ == "__main__":
    start_clubs_service()
