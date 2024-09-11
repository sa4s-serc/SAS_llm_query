from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class WellnessTipsService(MicroserviceBase):
    def __init__(self):
        super().__init__("WellnessTips", microservice_ports['health_wellness_tips'])

        @self.app.get("/data")
        async def get_data():
            return self._get_wellness_tip()

    def _get_wellness_tip(self):
        tips = [
            "Remember to stay hydrated!",
            "Take a 5-minute break every hour of studying",
            "Don't forget to eat breakfast before class",
            "Aim for 7-9 hours of sleep each night",
            "Practice deep breathing to reduce stress"
        ]
        return {"wellness_tip": random.choice(tips)}

def start_wellness_tips_service():
    service = WellnessTipsService()
    service.start()

if __name__ == "__main__":
    start_wellness_tips_service()
