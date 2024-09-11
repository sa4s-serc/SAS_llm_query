from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random
from app.utils.logger import setup_logger

logger = setup_logger('FitnessService')

class FitnessService(MicroserviceBase):
    def __init__(self):
        try:
            port = microservice_ports['health_fitness']
            logger.info(f"Initializing FitnessService on port {port}")
            super().__init__("Fitness", port)
        except Exception as e:
            logger.error(f"Error initializing FitnessService: {str(e)}", exc_info=True)
            raise

        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for fitness data")
            return self._get_fitness_suggestion()

    def _get_fitness_suggestion(self):
        suggestions = [
            "Try a 20-minute jog around campus",
            "Join a yoga session at the gym",
            "Take the stairs instead of the elevator today",
            "Do a quick 10-minute workout between classes",
            "Go for a bike ride this evening"
        ]
        suggestion = random.choice(suggestions)
        logger.info(f"Generated fitness suggestion: {suggestion}")
        return {"fitness_suggestion": suggestion}

def start_fitness_service():
    try:
        logger.info("Starting FitnessService")
        service = FitnessService()
        service.start()
    except Exception as e:
        logger.error(f"Error starting FitnessService: {str(e)}", exc_info=True)

if __name__ == "__main__":
    start_fitness_service()
