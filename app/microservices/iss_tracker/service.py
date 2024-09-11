from app.microservices.base import MicroserviceBase
from app.config import microservice_ports
import requests


class ISSTrackerService(MicroserviceBase):
    def __init__(self):
        super().__init__("ISSTracker", microservice_ports["resource_iss_tracker"])

        @self.app.get("/data")
        async def get_data():
            return self._get_iss_location()

    def _get_iss_location(self):
        url = "http://api.open-notify.org/iss-now.json"
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                "latitude": float(data["iss_position"]["latitude"]),
                "longitude": float(data["iss_position"]["longitude"]),
                "timestamp": data["timestamp"],
            }
        except requests.RequestException as e:
            self.logger.error(f"Error fetching ISS location: {e}")
            return {"error": "Unable to fetch ISS location"}


def start_iss_tracker_service():
    service = ISSTrackerService()
    service.start()


if __name__ == "__main__":
    start_iss_tracker_service()
