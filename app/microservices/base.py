from fastapi import FastAPI
import uvicorn
from app.utils.logger import setup_logger
from app.utils.port_manager import get_service_port, update_service_info


class MicroserviceBase:
    def __init__(self, name: str, port: int):
        self.app = FastAPI()
        self.name = name
        self.port = port
        self.logger = setup_logger(f"Microservice-{name}")

    def start(self):
        self.logger.info(f"Starting {self.name} microservice on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    # TODO: check the use of this paradigm
    @classmethod
    def create(cls, name: str):
        port = get_service_port(name)
        return cls(name, port)

    def update_info(self, description: str, dependencies: list):
        update_service_info(self.name, description, dependencies)
