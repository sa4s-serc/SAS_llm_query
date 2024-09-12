from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("HumidityService")


class HumidityService(MicroserviceBase):
    def __init__(self):
        super().__init__("humidity_service")

        self.update_service_info(
            description="Provides current humidity levels", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for humidity data")
            return self._get_humidity()

    # Service-specific logic
    def _get_humidity(self):
        humidity = round(random.uniform(30, 70), 1)
        logger.info(f"Generated humidity data: {humidity}")
        return {"humidity": humidity}


def start_humidity_service():
    service = HumidityService()
    service.run()


if __name__ == "__main__":
    start_humidity_service()
