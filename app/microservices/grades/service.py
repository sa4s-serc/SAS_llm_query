from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class GradesService(MicroserviceBase):
    def __init__(self):
        super().__init__("Grades", microservice_ports['academic_grades'])

        @self.app.get("/data")
        async def get_data():
            return self._get_grades()

    def _get_grades(self):
        subjects = ["Math", "Computer Science", "Physics", "English", "History"]
        return {subject: random.randint(60, 100) for subject in random.sample(subjects, 3)}

def start_grades_service():
    service = GradesService()
    service.start()

if __name__ == "__main__":
    start_grades_service()
