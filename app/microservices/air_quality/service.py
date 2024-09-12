from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("AirQualityService")


class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("air_quality_service")

        self.update_service_info(
            description="Provides air quality information", dependencies=[]
        )

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for air quality data")
            return self._get_air_quality()

    # Service-specific logic
    def _get_air_quality(self):
        aqi = random.randint(0, 500)
        if aqi <= 50:
            status = "Good"
        elif aqi <= 100:
            status = "Moderate"
        elif aqi <= 150:
            status = "Unhealthy for Sensitive Groups"
        elif aqi <= 200:
            status = "Unhealthy"
        elif aqi <= 300:
            status = "Very Unhealthy"
        else:
            status = "Hazardous"
        logger.info(f"Generated air quality data: AQI {aqi}, Status {status}")
        return {"aqi": aqi, "status": status}


def start_air_quality_service():
    service = AirQualityService()
    service.run()


if __name__ == "__main__":
    start_air_quality_service()
