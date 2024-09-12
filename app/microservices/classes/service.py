from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("ClassesService")


class ClassesService(MicroserviceBase):
    def __init__(self):
        super().__init__("classes_service")

        self.update_service_info(
            description="Provides information on class schedules", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for class schedule data")
            return self._get_classes()

    # Service-specific logic
    def _get_classes(self):
        classes = [
            "9:00 AM - Math",
            "11:00 AM - Computer Science",
            "2:00 PM - Physics",
            "4:00 PM - English Literature",
            "6:00 PM - History",
        ]
        selected_classes = random.sample(classes, 3)
        logger.info(f"Generated class schedule data: {selected_classes}")
        return {"classes": selected_classes}


def start_classes_service():
    service = ClassesService()
    service.run()


if __name__ == "__main__":
    start_classes_service()
