from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("AssignmentsService")


class AssignmentsService(MicroserviceBase):
    def __init__(self):
        super().__init__("assignments_service")

        self.update_service_info(
            description="Provides assignment information", dependencies=[]
        )

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for assignments data")
            return self._get_assignments()

    # Service-specific logic
    def _get_assignments(self):
        assignments = [
            "Math homework due in 2 days",
            "CS project due next week",
            "Physics lab report due tomorrow",
            "English essay due in 3 days",
            "History presentation next Monday",
        ]
        selected_assignments = random.sample(assignments, 2)
        logger.info(f"Generated assignments data: {selected_assignments}")
        return {"assignments": selected_assignments}


def start_assignments_service():
    service = AssignmentsService()
    service.run()


if __name__ == "__main__":
    start_assignments_service()
