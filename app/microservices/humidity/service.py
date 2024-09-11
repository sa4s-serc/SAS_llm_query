from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class HumidityService(MicroserviceBase):
    def __init__(self):
        super().__init__("Humidity", microservice_ports['environmental_humidity'])

        @self.app.get("/data")
        async def get_data():
            return self._get_humidity()

    def _get_humidity(self):
        return {"humidity": round(random.uniform(30, 70), 1)}

def start_humidity_service():
    service = HumidityService()
    service.start()

if __name__ == "__main__":
    start_humidity_service()
