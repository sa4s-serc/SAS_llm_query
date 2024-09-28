import os
import subprocess
import shutil
import app.config as config
from app.utils.logger import setup_logger
from app.utils.port_manager import get_port_manager


class AppGenerator:
    def __init__(self):
        self.logger = setup_logger("AppGenerator")
        self.port_manager = get_port_manager()
        self.used_ports = [10000]

    def generate_app(self, selected_services):
        self.logger.info(f"Generating app with services: {selected_services}")

        if config.GENERATED_APPS_DIR is None:
            self.logger.error(
                "GENERATED_APPS_DIR is None. Make sure config.set_paths() and config.setup() have been called."
            )
            raise ValueError(
                "GENERATED_APPS_DIR is not set. Configuration may not have been initialized properly."
            )

        port = self.used_ports[-1] - 1
        self.used_ports.append(port)
        app_dir = os.path.join(config.GENERATED_APPS_DIR, f"app_{port}")
        os.makedirs(app_dir, exist_ok=True)

        # Copy utility files
        utils_dir = os.path.join(app_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        shutil.copy(os.path.join(config.APP_DIR, "utils", "port_manager.py"), utils_dir)
        shutil.copy(os.path.join(config.APP_DIR, "utils", "logger.py"), utils_dir)

        # Copy services.toml
        shutil.copy(self.port_manager.services_file, app_dir)

        app_content = self._generate_app_content(selected_services, app_dir)
        app_file_path = os.path.join(app_dir, "app.py")

        with open(app_file_path, "w", encoding="utf-8") as f:
            f.write(app_content)

        self._run_app(app_file_path, port)
        return f"http://localhost:{port}"

    def _generate_app_content(self, selected_services, app_dir):
        content = f"""
import os
import sys

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

import streamlit as st
import requests
import logging
from utils.port_manager import get_port_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the working directory to the app directory
os.chdir(r'{app_dir}')

st.set_page_config(page_title="My IIIT Companion", page_icon="🏫", layout="wide")

st.title("My IIIT Companion")

port_manager = get_port_manager()

"""
        for service in selected_services:
            content += f"""
try:
    service_info = port_manager.get_service_info('{service}_service')
    if not service_info:
        raise ValueError(f"Service info not found for {service} service")
    port = service_info['port']
    logger.info(f"Attempting to connect to {service.capitalize()} service on port {{port}}")
    response = requests.get(f"http://localhost:{{port}}/data", timeout=5)
    response.raise_for_status()
    data = response.json()
    st.subheader('{service.capitalize()}')
    st.write(data)
    logger.info(f"Successfully connected to {service.capitalize()} service")
except ValueError as e:
    logger.error(str(e))
    st.error(str(e))
except requests.exceptions.ConnectionError as e:
    logger.error(f"Connection error for {service.capitalize()} service: {{e}}")
    st.error(f"Unable to connect to {service.capitalize()} service. Please ensure the service is running.")
except requests.exceptions.Timeout as e:
    logger.error(f"Timeout error for {service.capitalize()} service: {{e}}")
    st.error(f"Connection to {service.capitalize()} service timed out. The service might be overloaded or not responding.")
except requests.exceptions.RequestException as e:
    logger.error(f"Request error for {service.capitalize()} service: {{e}}")
    st.error(f"An error occurred while connecting to {service.capitalize()} service: {{str(e)}}")
"""
        return content

    def _run_app(self, app_file_path, port):
        self.logger.info(f"Running app at {app_file_path} on port {port}")
        subprocess.Popen(
            ["streamlit", "run", app_file_path, "--server.port", str(port)]
        )
