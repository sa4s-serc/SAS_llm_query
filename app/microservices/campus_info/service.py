from app.microservices.base import MicroserviceBase
from app.utils.logger import setup_logger
from app.utils.port_manager import get_service_port
import httpx
import asyncio

logger = setup_logger("CampusInfoService")


class CampusInfoService(MicroserviceBase):
    def __init__(self):
        super().__init__("campus_info_service")

        self.update_service_info(
            description="Provides combined campus information including events and cafeteria menu",
            dependencies=["events_service", "cafeteria_service"],
        )
        self.events_port = get_service_port("events_service")
        self.cafeteria_port = get_service_port("cafeteria_service")
        self.register_routes()

    def register_routes(self):
        @self.app.get("/data")
        async def get_data():
            logger.info("Received request for campus info data")
            return await self._get_campus_info()

    async def _get_events_data(self):
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:{self.events_port}/data"
            logger.info(f"Fetching events data from {url}")
            response = await client.get(url)
            return response.json()

    async def _get_cafeteria_data(self):
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:{self.cafeteria_port}/data"
            logger.info(f"Fetching cafeteria data from {url}")
            response = await client.get(url)
            return response.json()

    async def _get_campus_info(self):
        try:
            events_task = asyncio.create_task(self._get_events_data())
            cafeteria_task = asyncio.create_task(self._get_cafeteria_data())

            events_data, cafeteria_data = await asyncio.gather(
                events_task, cafeteria_task
            )

            campus_info = {
                "events": events_data.get("upcoming_events", []),
                "cafeteria_menu": cafeteria_data.get("menu", []),
            }

            logger.info(f"Generated campus info: {campus_info}")
            return {"campus_info": campus_info}
        except Exception as e:
            logger.error(f"Error fetching campus info: {str(e)}")
            return {"error": "Unable to fetch campus information at this time"}


def start_campus_info_service():
    service = CampusInfoService()
    service.run()


if __name__ == "__main__":
    start_campus_info_service()
