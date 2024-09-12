from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("LibraryService")


class LibraryService(MicroserviceBase):
    def __init__(self):
        super().__init__("library_service")

        self.update_service_info(
            description="Provides information on library availability", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for library status data")
            return self._get_library_status()

    # Service-specific logic
    def _get_library_status(self):
        availability = f"{random.randint(0, 100)}%"
        logger.info(f"Generated library availability data: {availability}")
        return {"availability": availability}


def start_library_service():
    service = LibraryService()
    service.run()


if __name__ == "__main__":
    start_library_service()
