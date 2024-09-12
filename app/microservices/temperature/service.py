from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("TemperatureService")


class TemperatureService(MicroserviceBase):
    def __init__(self):
        super().__init__("temperature_service")

        self.update_service_info(
            description="Provides current temperature readings", dependencies=[]
        )
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for temperature data")
            return self._get_temperature()

    # Service-specific logic
    def _get_temperature(self):
        temperature = round(random.uniform(20, 30), 1)
        logger.info(f"Generated temperature data: {temperature}")
        return {"temperature": temperature}


def start_temperature_service():
    service = TemperatureService()
    service.run()


if __name__ == "__main__":
    start_temperature_service()
