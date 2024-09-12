from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("WorkshopsService")


class WorkshopsService(MicroserviceBase):
    def __init__(self):
        super().__init__("workshops_service")

        self.update_service_info(
            description="Provides information on upcoming workshops", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for workshop data")
            return self._get_workshops()

    # Service-specific logic
    def _get_workshops(self):
        workshops = [
            "Resume Building Workshop next Tuesday",
            "Machine Learning Workshop this weekend",
            "Public Speaking Workshop on Wednesday",
            "Financial Literacy Seminar next month",
            "Design Thinking Workshop on Friday",
        ]
        workshop = random.choice(workshops)
        logger.info(f"Generated workshop data: {workshop}")
        return {"upcoming_workshop": workshop}


def start_workshops_service():
    service = WorkshopsService()
    service.run()


if __name__ == "__main__":
    start_workshops_service()
