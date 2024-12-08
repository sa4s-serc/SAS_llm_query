import toml
import os
from typing import Dict, List, Optional
from datetime import datetime

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
                services = toml.load(f)
                # Convert PID 0 to None for proper handling
                for service in services.values():
                    if service.get('pid', 0) == 0:
                        service['pid'] = None
                return services
        return {}

    def _save_services(self):
        # Convert None PIDs to 0 for TOML compatibility
        services_to_save = {}
        for name, service in self.services.items():
            service_copy = service.copy()
            if service_copy.get('pid') is None:
                service_copy['pid'] = 0
            services_to_save[name] = service_copy

        with open(self.services_file, "w") as f:
            toml.dump(services_to_save, f)

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
        enabled: bool = False,
        auto_start: bool = False
    ) -> int:
        if name in self.services:
            return self.services[name]["port"]

        if port is None:
            port = self.get_available_port(is_service=True)

        self.services[name] = {
            "port": port,
            "description": description,
            "dependencies": dependencies,
            "enabled": enabled,
            "pid": None,
            "auto_start": auto_start,
            "last_updated": datetime.now().isoformat()
        }
        self._save_services()
        return port

    def get_service_info(self, name: str) -> Dict:
        # Remove '_service' suffix if present
        name = name.replace('_service', '')
        # Try to find the service with or without '_service' suffix
        service_info = self.services.get(f"{name}_service", self.services.get(name, {}))
        # Ensure PID is None if 0
        if service_info.get('pid', 0) == 0:
            service_info['pid'] = None
        return service_info

    def update_service_info(
        self, 
        name: str, 
        description: str = None, 
        dependencies: List[str] = None,
        enabled: bool = None,
        pid: int = None,
        auto_start: bool = None
    ):
        if name not in self.services:
            raise ValueError(f"Service {name} not found")

        if description is not None:
            self.services[name]["description"] = description
        if dependencies is not None:
            self.services[name]["dependencies"] = dependencies
        if enabled is not None:
            self.services[name]["enabled"] = enabled
        if pid is not None:
            self.services[name]["pid"] = pid
        if auto_start is not None:
            self.services[name]["auto_start"] = auto_start
            
        self.services[name]["last_updated"] = datetime.now().isoformat()
        self._save_services()

    def enable_service(self, name: str, pid: Optional[int] = None):
        """Enable a service and optionally set its PID"""
        if name not in self.services:
            raise ValueError(f"Service {name} not found")
        
        self.services[name]["enabled"] = True
        self.services[name]["pid"] = pid
        self.services[name]["last_updated"] = datetime.now().isoformat()
        self._save_services()

    def disable_service(self, name: str):
        """Disable a service and clear its PID"""
        if name not in self.services:
            raise ValueError(f"Service {name} not found")
        
        self.services[name]["enabled"] = False
        self.services[name]["pid"] = None
        self.services[name]["last_updated"] = datetime.now().isoformat()
        self._save_services()

    def is_service_enabled(self, name: str) -> bool:
        """Check if a service is enabled"""
        service = self.get_service_info(name)
        return service.get("enabled", False)

    def get_service_pid(self, name: str) -> Optional[int]:
        """Get the PID of a running service"""
        service = self.get_service_info(name)
        pid = service.get("pid", 0)
        return None if pid == 0 else pid

    def get_auto_start_services(self) -> List[str]:
        """Get list of services configured for auto-start"""
        return [name for name, info in self.services.items() 
                if info.get("auto_start", False)]

    def get_required_services(self, app_services: List[str]) -> List[str]:
        """Get list of services required for an app, including dependencies"""
        required = set(app_services)
        for service in app_services:
            service_info = self.get_service_info(service)
            if service_info and "dependencies" in service_info:
                required.update(service_info["dependencies"])
        return list(required)

    def release_app_port(self, port: int):
        if port in self.app_ports:
            self.app_ports.remove(port)
        else:
            raise ValueError(f"App port {port} not found")

    def get_all_services(self) -> Dict[str, Dict]:
        services = {}
        for name, service in self.services.items():
            service_copy = service.copy()
            if service_copy.get('pid', 0) == 0:
                service_copy['pid'] = None
            services[name] = service_copy
        return services


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
    name: str, 
    description: str = None, 
    dependencies: List[str] = None,
    enabled: bool = None,
    pid: int = None,
    auto_start: bool = None
):
    get_port_manager().update_service_info(
        name, 
        description, 
        dependencies,
        enabled,
        pid,
        auto_start
    )
