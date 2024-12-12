import os
import json
import psutil
import subprocess
import signal
from typing import Dict, Optional, List
from app.utils.logger import setup_logger
from app.utils.port_manager import get_port_manager
import toml
from datetime import datetime

logger = setup_logger("ServiceManager")

class ServiceManager:
    def __init__(self):
        self.port_manager = get_port_manager()
        self.logger = logger
        self.services_file = "app/services.toml"
        self.services_config = self.load_services_config()

    def load_services_config(self) -> Dict:
        """Load services configuration from TOML file"""
        try:
            if os.path.exists(self.services_file):
                with open(self.services_file, 'r') as f:
                    return toml.load(f)
            else:
                self.logger.warning(f"Services file not found: {self.services_file}")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading services config: {str(e)}")
            return {}

    def get_available_services(self) -> List[str]:
        """Get list of all available services"""
        try:
            return list(self.services_config.keys())
        except Exception as e:
            self.logger.error(f"Error getting available services: {str(e)}")
            return []

    def get_service_info(self, service_name: str) -> Optional[Dict]:
        """Get information about a specific service"""
        try:
            return self.services_config.get(service_name)
        except Exception as e:
            self.logger.error(f"Error getting service info for {service_name}: {str(e)}")
            return None

    def update_service_status(self, service_name: str, enabled: bool, pid: Optional[int] = None) -> bool:
        """Update service status in the configuration"""
        try:
            if service_name in self.services_config:
                self.services_config[service_name]["enabled"] = enabled
                if pid is not None:
                    self.services_config[service_name]["pid"] = pid
                self.services_config[service_name]["last_updated"] = datetime.now().isoformat()
                self.save_services_config()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating service status for {service_name}: {str(e)}")
            return False

    def save_services_config(self) -> bool:
        """Save current services configuration to TOML file"""
        try:
            with open(self.services_file, 'w') as f:
                toml.dump(self.services_config, f)
            return True
        except Exception as e:
            self.logger.error(f"Error saving services config: {str(e)}")
            return False

    def is_service_running(self, service_name: str) -> bool:
        """Check if a service is currently running"""
        try:
            service_info = self.get_service_info(service_name)
            if not service_info:
                return False
            
            pid = service_info.get("pid")
            if not pid:
                return False

            # Check if process is running
            return psutil.pid_exists(pid)
        except Exception as e:
            self.logger.error(f"Error checking service status for {service_name}: {str(e)}")
            return False

    def get_service_description(self, service_name: str) -> str:
        """Get the description of a service"""
        try:
            service_info = self.get_service_info(service_name)
            if service_info:
                return service_info.get("description", "No description available")
            return "Service not found"
        except Exception as e:
            self.logger.error(f"Error getting service description for {service_name}: {str(e)}")
            return "Error retrieving description"

    def get_service_status(self, service_name: str) -> Dict:
        """Get current status of a service"""
        service_info = self.port_manager.get_service_info(service_name)
        if not service_info:
            return {"status": "not_found"}

        pid = service_info.get("pid")
        enabled = service_info.get("enabled", False)

        # Check if process is actually running
        is_running = self._is_process_running(pid) if pid else False
        
        # Update PID in config if process is not running
        if pid and not is_running:
            self.port_manager.update_service_info(
                name=service_name,
                pid=None,
                enabled=False
            )

        return {
            "status": "running" if is_running else "stopped",
            "enabled": is_running
        }

    def get_all_services_status(self) -> Dict[str, Dict]:
        """Get status of all services"""
        services_status = {}
        for service_name in self.port_manager.get_all_services().keys():
            services_status[service_name] = self.get_service_status(service_name)
        return services_status

    def start_service(self, service_name: str, version: str = "original") -> Dict:
        """Start a specific service version"""
        try:
            service_info = self.port_manager.get_service_info(service_name)
            if not service_info:
                return {"success": False, "message": f"Service {service_name} not found"}

            current_status = self.get_service_status(service_name)
            if current_status["status"] == "running":
                return {"success": True, "message": f"Service {service_name} is already running"}

            # Kill any existing process with the same PID
            old_pid = service_info.get("pid")
            if old_pid:
                self._terminate_process_group(old_pid)

            # Get service path based on version
            service_path = self._get_service_path(service_name, version)
            if not service_path:
                return {"success": False, "message": f"{version} version of {service_name} not found"}

            # Start the service using Python
            cmd = ["python", "-m", service_path]
            process = subprocess.Popen(cmd, start_new_session=True)
            
            # Update service state with new PID
            self.port_manager.update_service_info(
                name=service_name,
                enabled=True,
                pid=process.pid
            )

            return {
                "success": True,
                "message": f"Started {version} version of {service_name}"
            }

        except Exception as e:
            self.logger.error(f"Error starting service {service_name}: {str(e)}")
            return {"success": False, "message": str(e)}

    def stop_service(self, service_name: str) -> Dict:
        """Stop a specific service"""
        try:
            service_info = self.port_manager.get_service_info(service_name)
            if not service_info:
                return {"success": False, "message": f"Service {service_name} not found"}

            current_status = self.get_service_status(service_name)
            if current_status["status"] != "running":
                return {"success": True, "message": f"Service {service_name} is not running"}

            pid = service_info.get("pid")
            if pid:
                # Kill the entire process group
                self._terminate_process_group(pid)
                
            # Update service state
            self.port_manager.update_service_info(
                name=service_name,
                enabled=False,
                pid=None
            )

            return {"success": True, "message": f"Stopped service {service_name}"}

        except Exception as e:
            self.logger.error(f"Error stopping service {service_name}: {str(e)}")
            return {"success": False, "message": str(e)}

    def _is_process_running(self, pid: Optional[int]) -> bool:
        """Check if a process is running"""
        if pid is None:
            return False
        try:
            process = psutil.Process(pid)
            return process.is_running() and process.status() != psutil.STATUS_ZOMBIE
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return False

    def _terminate_process_group(self, pid: int):
        """Terminate a process and its entire process group"""
        try:
            # Try to get the process group
            os.killpg(os.getpgid(pid), signal.SIGTERM)
            
            # Wait for termination
            try:
                os.waitpid(pid, os.WNOHANG)
                import time
                time.sleep(2)  # Give processes time to terminate
                
                # If still running, force kill
                if self._is_process_running(pid):
                    os.killpg(os.getpgid(pid), signal.SIGKILL)
            except (ProcessLookupError, ChildProcessError):
                pass  # Process already terminated
                
        except (ProcessLookupError, PermissionError) as e:
            # If we can't kill the group, try to kill just the process
            try:
                process = psutil.Process(pid)
                process.terminate()
                process.wait(timeout=3)
            except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                pass
            
        except Exception as e:
            self.logger.warning(f"Error terminating process {pid}: {str(e)}")

    def _get_service_path(self, service_name: str, version: str = "original") -> Optional[str]:
        """Get the correct import path for a service version"""
        if version == "original":
            if os.path.exists(f"app/microservices/{service_name}/service.py"):
                return f"app.microservices.{service_name}.service"
        elif version == "generated":
            if os.path.exists(f"app/generated_services/{service_name}/service.py"):
                return f"app.generated_services.{service_name}.service"
        return None

    def get_service_logs(self, service_name: str, lines: int = 100) -> List[str]:
        """Get recent logs for a service"""
        log_file = f"logs/{service_name}.log"
        if not os.path.exists(log_file):
            return []
        
        try:
            with open(log_file, 'r') as f:
                return f.readlines()[-lines:]
        except Exception as e:
            self.logger.error(f"Error reading logs for {service_name}: {str(e)}")
            return []