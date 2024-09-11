from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class ClassesService(MicroserviceBase):
    def __init__(self):
        super().__init__("Classes", microservice_ports['academic_classes'])

        @self.app.get("/data")
        async def get_data():
            return self._get_classes()

    def _get_classes(self):
        classes = [
            "9:00 AM - Math",
            "11:00 AM - Computer Science",
            "2:00 PM - Physics",
            "4:00 PM - English Literature",
            "6:00 PM - History"
        ]
        return random.sample(classes, 3)

def start_classes_service():
    service = ClassesService()
    service.start()

if __name__ == "__main__":
    start_classes_service()
