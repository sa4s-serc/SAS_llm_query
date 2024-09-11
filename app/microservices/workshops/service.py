from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class WorkshopsService(MicroserviceBase):
    def __init__(self):
        super().__init__("Workshops", microservice_ports['event_workshops'])

        @self.app.get("/data")
        async def get_data():
            return self._get_workshops()

    def _get_workshops(self):
        workshops = [
            "Resume Building Workshop next Tuesday",
            "Machine Learning Workshop this weekend",
            "Public Speaking Workshop on Wednesday",
            "Financial Literacy Seminar next month",
            "Design Thinking Workshop on Friday"
        ]
        return {"upcoming_workshop": random.choice(workshops)}

def start_workshops_service():
    service = WorkshopsService()
    service.start()

if __name__ == "__main__":
    start_workshops_service()
