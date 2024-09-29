from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("FitnessService")


class FitnessService(MicroserviceBase):
    def __init__(self):
        super().__init__("fitness_service")

        self.update_service_info(
            description="Provides fitness suggestions and tracking", dependencies=[]
        )

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for fitness data")
            return self._get_fitness_suggestion()

    # Service-specific logic
    def _get_fitness_suggestion(self):
        suggestions = [
            "Try a 20-minute jog around campus",
            "Join a yoga session at the gym",
            "Take the stairs instead of the elevator today",
            "Do a quick 10-minute workout between classes",
            "Go for a bike ride this evening",
        ]
        suggestion = random.choice(suggestions)
        logger.info(f"Generated fitness suggestion: {suggestion}")
        return {"fitness_suggestion": suggestion}


def start_fitness_service():
    service = FitnessService()
    service.run()


if __name__ == "__main__":
    start_fitness_service()
