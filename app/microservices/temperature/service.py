from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class TemperatureService(MicroserviceBase):
    def __init__(self):
        super().__init__("Temperature", microservice_ports['environmental_temperature'])

        @self.app.get("/data")
        async def get_data():
            return self._get_temperature()

    def _get_temperature(self):
        return {"temperature": round(random.uniform(20, 30), 1)}

def start_temperature_service():
    service = TemperatureService()
    service.start()

if __name__ == "__main__":
    start_temperature_service()
