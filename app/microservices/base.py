from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any
from app.utils.port_manager import get_service_port, update_service_info
from app.utils.logger import setup_logger


class MicroserviceBase:
    def __init__(self, name: str):
        self.name = name
        self.port = get_service_port(name)
        self.app = FastAPI()
        self.logger = setup_logger(f"Microservice-{name}")

        self.logger.info(f"Initializing {self.name} microservice on port {self.port}")

    def start(self):
        self.logger.info(f"Starting {self.name} microservice on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def register_routes(self):
        # override by child classes
        pass

    def update_service_info(self, description: str, dependencies: list = None):
        if dependencies is None:
            dependencies = []
        update_service_info(self.name, description, dependencies)
        self.logger.info(f"Updated service info for {self.name}")

    def run(self):
        self.register_routes()
        self.start()

    async def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # This method should be implemented by child classes
        raise NotImplementedError("This method should be implemented by child classes")
