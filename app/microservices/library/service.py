from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class LibraryService(MicroserviceBase):
    def __init__(self):
        super().__init__("Library", microservice_ports['resource_library'])

        @self.app.get("/data")
        async def get_data():
            return self._get_library_status()

    def _get_library_status(self):
        return {"availability": f"{random.randint(0, 100)}%"}

def start_library_service():
    service = LibraryService()
    service.start()

if __name__ == "__main__":
    start_library_service()
