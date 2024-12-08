import os
import sys
import importlib
import multiprocessing
import signal
import time
from typing import Dict, List
from app.utils.logger import setup_logger
from app.utils.port_manager import get_port_manager

logger = setup_logger("run_microservices")

def import_service_module(service_name: str):
    """Import a service module dynamically"""
    try:
        module_path = f"app.microservices.{service_name}.service"
        logger.info(f"Importing module {module_path} for {service_name}")
        return importlib.import_module(module_path)
    except ImportError as e:
        logger.error(f"Error importing {service_name} module: {str(e)}")
        return None

def get_start_function(module, service_name: str):
    """Get the start function for a service"""
    try:
        logger.info(f"Getting start function for {service_name}")
        function_name = f"start_{service_name}_service"
        return getattr(module, function_name)
    except AttributeError as e:
        logger.error(f"Error getting start function for {service_name}: {str(e)}")
        return None

def start_service(service_name: str):
    """Start a single service"""
    try:
        logger.info(f"Starting {service_name} service")
        module = import_service_module(service_name)
        if module:
            start_func = get_start_function(module, service_name)
            if start_func:
                start_func()
    except Exception as e:
        logger.error(f"Error starting {service_name} service: {str(e)}")

def run_services():
    """Run all enabled services"""
    port_manager = get_port_manager()
    processes: Dict[str, multiprocessing.Process] = {}

    def signal_handler(signum, frame):
        logger.info("Received shutdown signal. Stopping all services...")
        for service_name, process in processes.items():
            logger.info(f"Stopping {service_name}...")
            process.terminate()
            port_manager.disable_service(service_name)
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Start enabled services
        for service_name, service_info in port_manager.get_all_services().items():
            if service_info.get("enabled", False):
                process = multiprocessing.Process(
                    target=start_service,
                    args=(service_name,),
                    name=f"{service_name}_process"
                )
                process.start()
                processes[service_name] = process
                port_manager.update_service_info(
                    name=service_name,
                    pid=process.pid,
                    enabled=True
                )
                logger.info(f"Started {service_name} service with PID {process.pid}")

        # Monitor processes
        while True:
            for service_name, process in list(processes.items()):
                if not process.is_alive():
                    logger.warning(f"Service {service_name} died. Restarting...")
                    port_manager.disable_service(service_name)
                    processes.pop(service_name)
                    
                    # Only restart if service is still enabled in config
                    if port_manager.is_service_enabled(service_name):
                        new_process = multiprocessing.Process(
                            target=start_service,
                            args=(service_name,),
                            name=f"{service_name}_process"
                        )
                        new_process.start()
                        processes[service_name] = new_process
                        port_manager.update_service_info(
                            name=service_name,
                            pid=new_process.pid,
                            enabled=True
                        )
                        logger.info(f"Restarted {service_name} service with PID {new_process.pid}")
            
            time.sleep(5)  # Check every 5 seconds

    except Exception as e:
        logger.error(f"Error in run_services: {str(e)}")
        signal_handler(None, None)

if __name__ == "__main__":
    run_services()

