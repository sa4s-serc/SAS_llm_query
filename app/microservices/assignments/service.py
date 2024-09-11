from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class AssignmentsService(MicroserviceBase):
    def __init__(self):
        super().__init__("Assignments", microservice_ports['academic_assignments'])

        @self.app.get("/data")
        async def get_data():
            return self._get_assignments()

    def _get_assignments(self):
        assignments = [
            "Math homework due in 2 days",
            "CS project due next week",
            "Physics lab report due tomorrow",
            "English essay due in 3 days",
            "History presentation next Monday"
        ]
        return random.sample(assignments, 2)

def start_assignments_service():
    service = AssignmentsService()
    service.start()

if __name__ == "__main__":
    start_assignments_service()
