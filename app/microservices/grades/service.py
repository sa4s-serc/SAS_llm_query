from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("GradesService")


class GradesService(MicroserviceBase):
    def __init__(self):
        super().__init__("grades_service")

        self.update_service_info(
            description="Provides student grades for various subjects", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for grades data")
            return self._get_grades()

    # Service-specific logic
    def _get_grades(self):
        subjects = ["Math", "Computer Science", "Physics", "English", "History"]
        grades = {
            subject: random.randint(60, 100) for subject in random.sample(subjects, 3)
        }
        logger.info(f"Generated grades data: {grades}")
        return grades


def start_grades_service():
    service = GradesService()
    service.run()


if __name__ == "__main__":
    start_grades_service()
