from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("StudyRoomsService")


class StudyRoomsService(MicroserviceBase):
    def __init__(self):
        super().__init__("study_rooms_service")

        self.update_service_info(
            description="Provides information on available study rooms", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for study rooms data")
            return self._get_study_rooms()

    # Service-specific logic
    def _get_study_rooms(self):
        available_rooms = random.randint(1, 10)
        logger.info(f"Generated study rooms data: {available_rooms}")
        return {"available_rooms": available_rooms}


def start_study_rooms_service():
    service = StudyRoomsService()
    service.run()


if __name__ == "__main__":
    start_study_rooms_service()
