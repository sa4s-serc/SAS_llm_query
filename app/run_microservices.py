import os
import sys
import importlib
import threading
import time
import psutil
import requests
from app.microservices.travel_options.service import start_travel_options_service
from app.microservices.crowd_monitor.service import start_crowd_monitor_service
from app.microservices.event_notifier.service import start_event_notifier_service
from app.microservices.historical_info.service import start_historical_info_service
from app.microservices.air_quality.service import start_air_quality_service
from app.microservices.water_quality.service import start_water_quality_service
from app.microservices.restaurant_finder.service import start_restaurant_finder_service
from app.microservices.ticket_purchase.service import start_ticket_purchase_service
from app.microservices.exhibition_tracker.service import start_exhibition_tracker_service
import multiprocessing

# Get the absolute path of the current file
current_file = os.path.abspath(__file__)

# Get the root directory of the project (one level up from the current file)
project_root = os.path.dirname(os.path.dirname(current_file))

# Add the project root to the Python path
sys.path.insert(0, project_root)

# Import the config module
import app.config as config

# Set up the configuration
config.set_paths(os.path.dirname(current_file))
config.setup()

# Now we can access the configuration variables
MICROSERVICES_DIR = config.MICROSERVICES_DIR

# Now import the logger and PortManager
from app.utils.logger import setup_logger
from app.utils.port_manager import PortManager

logger = setup_logger("run_microservices")
port_manager = PortManager()


def run_microservice(module_name, service_name):
    try:
        logger.info(f"Importing module {module_name} for {service_name}")
        module = importlib.import_module(module_name)

        logger.info(f"Getting start function for {service_name}")
        start_function = getattr(module, f"start_{service_name.lower()}_service")

        logger.info(f"Starting {service_name} service")
        start_function()

    except ImportError as e:
        logger.error(
            f"Error importing module for {service_name}: {str(e)}", exc_info=True
        )
    except AttributeError as e:
        logger.error(
            f"Error finding start function for {service_name}: {str(e)}", exc_info=True
        )
    except Exception as e:
        logger.error(f"Error starting {service_name} service: {str(e)}", exc_info=True)


def discover_services(directory):
    services = {}
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and item != "__pycache__":
            service_file = os.path.join(item_path, "service.py")
            if os.path.exists(service_file):
                module_name = f"app.microservices.{item}.service"
                services[item.lower()] = module_name
    return services


def check_dependency_health(dependency):
    service_info = port_manager.get_service_info(dependency)
    if not service_info:
        logger.error(f"Service info not found for dependency: {dependency}")
        return False
    port = service_info["port"]
    try:
        response = requests.get(f"http://localhost:{port}/data", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_service(service_name, module_name):
    service_info = port_manager.get_service_info(service_name)
    if service_info and "dependencies" in service_info:
        for dependency in service_info["dependencies"]:
            retry_count = 0
            while retry_count < 3:  # Try 3 times
                if check_dependency_health(dependency):
                    break
                logger.warning(
                    f"Dependency {dependency} not healthy for {service_name}. Retrying in 5 seconds..."
                )
                time.sleep(5)
                retry_count += 1
            else:
                logger.error(
                    f"Failed to start {service_name} due to unhealthy dependency: {dependency}"
                )
                return None

    thread = threading.Thread(target=run_microservice, args=(module_name, service_name))
    thread.start()
    return thread


def run_all_microservices():
    services = discover_services(config.MICROSERVICES_DIR)
    threads = []

    # Start services without dependencies first
    for service_name, module_name in list(services.items()):
        service_info = port_manager.get_service_info(service_name)
        if (
            not service_info
            or "dependencies" not in service_info
            or not service_info["dependencies"]
        ):
            thread = run_service(service_name, module_name)
            if thread:
                threads.append(thread)
                del services[service_name]
            time.sleep(1)

    # Start services with dependencies
    while services:
        for service_name, module_name in list(services.items()):
            thread = run_service(service_name, module_name)
            if thread:
                threads.append(thread)
                del services[service_name]
            time.sleep(0.1)

        if services:
            time.sleep(1)  # Wait before checking again

    for thread in threads:
        thread.join()


def run_all_services():
    services = [
        start_travel_options_service,
        start_crowd_monitor_service,
        start_event_notifier_service,
        start_historical_info_service,
        start_air_quality_service,
        start_water_quality_service,
        start_restaurant_finder_service,
        start_ticket_purchase_service,
        start_exhibition_tracker_service
    ]

    processes = []
    for service in services:
        p = multiprocessing.Process(target=service)
        p.start()
        processes.append(p)

    for p in processes:
        p.join()


if __name__ == "__main__":
    logger.info("Starting all microservices...")
    # run_all_microservices()
    run_all_services()

    logger.info("All microservices started")

    # Keep the script running and periodically log running services
    while True:
        time.sleep(60)
        logger.info("Currently running microservices:")
        for process in psutil.process_iter(["pid", "name", "cmdline"]):
            if "python" in process.info[
                "name"
            ].lower() and "run_microservices.py" in " ".join(process.info["cmdline"]):
                logger.info(
                    f"PID: {process.info['pid']}, Command: {' '.join(process.info['cmdline'])}"
                )

