import os
import sys
import importlib
import threading
import time
import psutil
import requests
import yaml

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
microservice_ports = config.microservice_ports

# Now import the logger
from app.utils.logger import setup_logger
from app.utils.port_manager import (
    get_port,
    update_port_map,
    PORT_MAP_FILE,
    clean_port_map,
)

logger = setup_logger("run_microservices")


def load_dependencies():
    dependency_file = os.path.join(project_root, "app", "dependencies.yaml")
    if os.path.exists(dependency_file):
        with open(dependency_file, "r") as f:
            return yaml.safe_load(f)["services"]
    return {}


dependencies = load_dependencies()


def run_microservice(module_name, service_name, port):
    try:
        logger.info(f"Importing module {module_name} for {service_name}")
        module = importlib.import_module(module_name)

        logger.info(f"Getting start function for {service_name}")
        start_function = getattr(module, f"start_{service_name.lower()}_service")

        logger.info(f"Starting {service_name} service on port {port}")
        update_port_map(service_name.lower(), port)
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


def discover_services(directory, module_prefix="app.microservices", path_prefix=""):
    services = {}
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            services.update(
                discover_services(
                    item_path,
                    f"{module_prefix}.{item}",
                    f"{path_prefix}{item.lower()}_",
                )
            )
        elif item.endswith(".py") and not item.startswith("__") and item != "base.py":
            service_name = os.path.splitext(item)[0]
            module_name = f"{module_prefix}.{service_name}"
            port_key = f"{path_prefix}{service_name.lower()}"
            port = config.get_port(port_key)
            if port is not None:
                services[port_key] = (module_name, service_name, port)
            else:
                logger.error(f"Port not found for service: {port_key}")
    return services


def check_dependency_health(dependency):
    port = get_port(dependency)
    if port is None:
        logger.error(f"Port not found for dependency: {dependency}")
        return False
    try:
        response = requests.get(f"http://localhost:{port}/data", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


def run_service(service):
    module_name, service_name, port = service
    service_key = f"{module_name.split('.')[-2].lower()}_{service_name.lower()}"

    if service_key in dependencies:
        for dependency in dependencies[service_key]["depends_on"]:
            retry_count = 0
            while retry_count < 3:  # Try 3 times
                if check_dependency_health(dependency):
                    break
                logger.warning(
                    f"Dependency {dependency} not healthy for {service_key}. Retrying in 5 seconds..."
                )
                time.sleep(5)
                retry_count += 1
            else:
                logger.error(
                    f"Failed to start {service_key} due to unhealthy dependency: {dependency}"
                )
                return None

    thread = threading.Thread(
        target=run_microservice, args=(module_name, service_name, port)
    )
    thread.start()
    return thread


def run_all_microservices():
    # Clear the existing port map
    if os.path.exists(PORT_MAP_FILE):
        os.remove(PORT_MAP_FILE)

    services = discover_services(config.MICROSERVICES_DIR)
    threads = []

    # Start services without dependencies first
    for service_key, service in list(services.items()):
        if service_key not in dependencies:
            thread = run_service(service)
            if thread:
                threads.append(thread)
                del services[service_key]
            time.sleep(0.1)

    # Start services with dependencies
    while services:
        for service_key, service in list(services.items()):
            thread = run_service(service)
            if thread:
                threads.append(thread)
                del services[service_key]
            time.sleep(0.1)

        if services:
            time.sleep(1)  # Wait before checking again

    for thread in threads:
        thread.join()

    # Clean and standardize the port map after all services have started
    clean_port_map()


if __name__ == "__main__":
    logger.info("Starting all microservices...")
    run_all_microservices()
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
