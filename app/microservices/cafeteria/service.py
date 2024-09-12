from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
import random

logger = setup_logger("CafeteriaService")


class CafeteriaService(MicroserviceBase):
    def __init__(self):
        super().__init__("cafeteria_service")

        self.update_service_info(
            description="Provides cafeteria menu options", dependencies=[]
        )

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for cafeteria menu data")
            return self._get_menu()

    # Service-specific logic
    def _get_menu(self):
        meals = [
            "Pasta",
            "Pizza",
            "Salad",
            "Burger",
            "Soup",
            "Sandwich",
            "Curry",
            "Stir Fry",
        ]
        selected_meals = random.sample(meals, 3)
        logger.info(f"Generated cafeteria menu: {selected_meals}")
        return {"menu": selected_meals}


def start_cafeteria_service():
    service = CafeteriaService()
    service.run()


if __name__ == "__main__":
    start_cafeteria_service()
