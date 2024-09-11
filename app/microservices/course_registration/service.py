from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random
import requests


class CourseRegistrationService(MicroserviceBase):
    def __init__(self):
        super().__init__(
            "CourseRegistration", microservice_ports["academic_course_registration"]
        )

        @self.app.get("/data")
        async def get_data():
            return self._get_course_registration_info()

    def _get_course_registration_info(self):
        grades = self._get_grades()
        library_status = self._get_library_status()

        courses = [
            "Advanced Algorithms",
            "Machine Learning",
            "Data Structures",
            "Computer Networks",
            "Database Systems",
        ]
        available_courses = random.sample(courses, 3)

        return {
            "available_courses": available_courses,
            "grades": grades,
            "library_status": library_status,
        }

    def _get_grades(self):
        try:
            response = requests.get(
                f"http://localhost:{microservice_ports['academic_grades']}/data"
            )
            return response.json()
        except:
            return {"Error": "Unable to fetch grades"}

    def _get_library_status(self):
        try:
            response = requests.get(
                f"http://localhost:{microservice_ports['resource_library']}/data"
            )
            return response.json()
        except:
            return {"Error": "Unable to fetch library status"}


def start_course_registration_service():
    service = CourseRegistrationService()
    service.start()


if __name__ == "__main__":
    start_course_registration_service()
