from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import random

class CafeteriaService(MicroserviceBase):
    def __init__(self):
        super().__init__("Cafeteria", microservice_ports['resource_cafeteria'])

        @self.app.get("/data")
        async def get_data():
            return self._get_menu()

    def _get_menu(self):
        meals = ["Pasta", "Pizza", "Salad", "Burger", "Soup", "Sandwich", "Curry", "Stir Fry"]
        return {"menu": random.sample(meals, 3)}

def start_cafeteria_service():
    service = CafeteriaService()
    service.start()

if __name__ == "__main__":
    start_cafeteria_service()
