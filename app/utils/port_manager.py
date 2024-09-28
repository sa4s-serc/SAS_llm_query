import toml
import os
from typing import Dict, List, Optional

MIN_PORT: int = 9000
MAX_PORT: int = 9999


class PortManager:
    def __init__(self, services_file: str = "services.toml"):
        self.services_file = os.path.join("app", services_file)

    def _read_services(self) -> Dict:
        services_file = os.path.join(os.getcwd(), "services.toml")
        if os.path.exists(services_file):
            with open(services_file, "r") as f:
                services = toml.load(f)
                return services
        return {}

    def _write_services(self, services: Dict):
        with open(self.services_file, "w") as f:
            toml.dump(services, f)

    def get_available_port(self) -> int:
        services = self._read_services()
        if not services:
            return MIN_PORT
        last_port = max(service["port"] for service in services.values())
        new_port = last_port + 1
        if new_port > MAX_PORT:
            raise ValueError("No available ports")
        return new_port

    def register_service(
        self,
        name: str,
        port: Optional[int] = None,
        description: str = "",
        dependencies: List[str] = [],
    ) -> int:
        services = self._read_services()
        if name in services:
            return services[name]["port"]

        if port is None:
            port = self.get_available_port()

        services[name] = {
            "port": port,
            "description": description,
            "dependencies": dependencies,
        }
        self._write_services(services)
        return port

    def get_service_info(self, name: str) -> Dict:
        services = self._read_services()
        return services.get(name, {})

    def update_service_info(
        self, name: str, description: str = None, dependencies: List[str] = None
    ):
        services = self._read_services()
        if name not in services:
            raise ValueError(f"Service {name} not found")

        if description is not None:
            services[name]["description"] = description
        if dependencies is not None:
            services[name]["dependencies"] = dependencies

        self._write_services(services)


# Global instance of PortManager
_port_manager = None


def get_port_manager():
    global _port_manager
    if _port_manager is None:
        _port_manager = PortManager()
    return _port_manager


def get_service_port(name: str) -> int:
    return get_port_manager().register_service(name)


def update_service_info(
    name: str, description: str = None, dependencies: List[str] = None
):
    get_port_manager().update_service_info(name, description, dependencies)
