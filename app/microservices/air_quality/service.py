from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class AirQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("AirQuality", microservice_ports['environmental_air_quality'])

        @self.app.get("/data")
        async def get_data():
            return self._get_air_quality()

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
        return {"aqi": aqi, "status": status}

def start_air_quality_service():
    service = AirQualityService()
    service.start()

if __name__ == "__main__":
    start_air_quality_service()
