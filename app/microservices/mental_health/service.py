from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class MentalHealthService(MicroserviceBase):
    def __init__(self):
        super().__init__("MentalHealth", microservice_ports['health_mental_health'])

        @self.app.get("/data")
        async def get_data():
            return self._get_mental_health_resource()

    def _get_mental_health_resource(self):
        resources = [
            "Counseling services available at Student Center",
            "Meditation app free for students: Calm",
            "Join the Mindfulness Club for stress relief techniques",
            "24/7 mental health hotline: 1-800-273-TALK",
            "Student support group meets every Wednesday at 5 PM"
        ]
        return {"mental_health_resource": random.choice(resources)}

def start_mental_health_service():
    service = MentalHealthService()
    service.start()

if __name__ == "__main__":
    start_mental_health_service()
