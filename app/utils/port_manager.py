import toml
import os
from typing import Dict, List, Optional

MIN_PORT: int = 9000
MAX_PORT: int = 9999


class PortManager:
    def __init__(self, services_file: str = "services.toml"):
        self.services_file = os.path.join(
            os.path.dirname(__file__), "..", "services.toml"
        )
        self.services = self._load_services()
        self.app_ports = set()

    def _load_services(self) -> Dict:
        if os.path.exists(self.services_file):
            with open(self.services_file, "r") as f:
                return toml.load(f)
        return {}

    def _save_services(self):
        with open(self.services_file, "w") as f:
            toml.dump(self.services, f)

    def get_available_port(self, is_service: bool = True) -> int:
        used_ports = set(service["port"] for service in self.services.values())
        used_ports.update(self.app_ports)

        for port in range(MIN_PORT, MAX_PORT + 1):
            if port not in used_ports:
                if is_service:
                    return port
                else:
                    self.app_ports.add(port)
                    return port
        raise ValueError("No available ports")

    def register_service(
        self,
        name: str,
        port: Optional[int] = None,
        description: str = "",
        dependencies: List[str] = [],
    ) -> int:
        if name in self.services:
            return self.services[name]["port"]

        if port is None:
            port = self.get_available_port(is_service=True)

        self.services[name] = {
            "port": port,
            "description": description,
            "dependencies": dependencies,
        }
        self._save_services()
        return port

    def get_service_info(self, name: str) -> Dict:
        return self.services.get(name, {})

    def update_service_info(
        self, name: str, description: str = None, dependencies: List[str] = None
    ):
        if name not in self.services:
            raise ValueError(f"Service {name} not found")

        if description is not None:
            self.services[name]["description"] = description
        if dependencies is not None:
            self.services[name]["dependencies"] = dependencies

        self._save_services()

    def release_app_port(self, port: int):
        if port in self.app_ports:
            self.app_ports.remove(port)
        else:
            raise ValueError(f"App port {port} not found")


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
