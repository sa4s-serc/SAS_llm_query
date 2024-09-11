from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class StudyRoomsService(MicroserviceBase):
    def __init__(self):
        super().__init__("StudyRooms", microservice_ports['resource_study_rooms'])

        @self.app.get("/data")
        async def get_data():
            return self._get_study_rooms()

    def _get_study_rooms(self):
        return {"available_rooms": random.randint(1, 10)}

def start_study_rooms_service():
    service = StudyRoomsService()
    service.start()

if __name__ == "__main__":
    start_study_rooms_service()
