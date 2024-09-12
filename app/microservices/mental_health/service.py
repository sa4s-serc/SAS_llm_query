from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("MentalHealthService")


class MentalHealthService(MicroserviceBase):
    def __init__(self):
        super().__init__("mental_health_service")

        self.update_service_info(
            description="Provides mental health resources and support", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for mental health resources")
            return self._get_mental_health_resource()

    # Service-specific logic
    def _get_mental_health_resource(self):
        resources = [
            "Counseling services available at Student Center",
            "Meditation app free for students: Calm",
            "Join the Mindfulness Club for stress relief techniques",
            "24/7 mental health hotline: 1-800-273-TALK",
            "Student support group meets every Wednesday at 5 PM",
        ]
        resource = random.choice(resources)
        logger.info(f"Generated mental health resource: {resource}")
        return {"mental_health_resource": resource}


def start_mental_health_service():
    service = MentalHealthService()
    service.run()


if __name__ == "__main__":
    start_mental_health_service()
