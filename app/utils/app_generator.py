import os
import subprocess
import shutil
import json
import app.config as config
from app.utils.logger import setup_logger
from app.utils.port_manager import get_port_manager
from app.templates.generated_app_template import GENERATED_APP_TEMPLATE


class AppGenerator:
    def __init__(self):
        self.logger = setup_logger("AppGenerator")
        self.port_manager = get_port_manager()
        self.used_ports = [10000]

    def generate_app(self, selected_services, parameters):
        self.logger.info(f"Generating app with services: {selected_services}")
        self.logger.info(f"Service parameters: {parameters}")

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

        self.logger.info(f"Created app directory: {app_dir}")

        # Copy utility files
        utils_dir = os.path.join(app_dir, "utils")
        os.makedirs(utils_dir, exist_ok=True)
        shutil.copy(os.path.join(config.APP_DIR, "utils", "port_manager.py"), utils_dir)
        shutil.copy(os.path.join(config.APP_DIR, "utils", "logger.py"), utils_dir)

        self.logger.info(f"Copied utility files to: {utils_dir}")

        # Copy services.toml
        services_toml_path = os.path.join(app_dir, "services.toml")
        shutil.copy(self.port_manager.services_file, services_toml_path)
        self.logger.info(f"Copied services.toml to: {services_toml_path}")

        # Log the contents of services.toml
        with open(services_toml_path, 'r') as f:
            self.logger.info(f"Contents of services.toml:\n{f.read()}")

        # Copy templates directory
        templates_dir = os.path.join(app_dir, "templates")
        os.makedirs(templates_dir, exist_ok=True)
        shutil.copy(
            os.path.join(config.APP_DIR, "templates", "generated_app_template.py"),
            templates_dir,
        )

        self.logger.info(f"Copied templates to: {templates_dir}")

        app_content = self._generate_app_content(selected_services, parameters, app_dir)
        app_file_path = os.path.join(app_dir, "app.py")

        with open(app_file_path, "w", encoding="utf-8") as f:
            f.write(app_content)

        self.logger.info(f"Generated app content and wrote to: {app_file_path}")

        self._run_app(app_file_path, port)
        return f"http://localhost:{port}"

    def _generate_app_content(self, selected_services, parameters, app_dir):
        service_content = ""
        for service in selected_services:
            service_content += self._generate_service_content(service, parameters.get(service, {}))

        debug_content = f"""
# Debugging information
selected_services = {json.dumps(selected_services)}
parameters = {json.dumps(parameters)}

st.sidebar.header("Debugging Information")
st.sidebar.write(f"Selected services: {{json.dumps(selected_services, indent=2)}}")
st.sidebar.write(f"Parameters: {{json.dumps(parameters, indent=2)}}")

# Log available services
available_services = port_manager.get_all_services()
st.sidebar.write(f"Available services: {{json.dumps(available_services, indent=2)}}")
logger.info(f"Available services: {{json.dumps(available_services, indent=2)}}")

# Log the contents of services.toml
with open('services.toml', 'r') as f:
    services_toml_content = f.read()
    st.sidebar.text_area("services.toml content:", services_toml_content, height=300)
    logger.info(f"services.toml content:\\n{{services_toml_content}}")

# Log the current working directory
current_dir = os.getcwd()
st.sidebar.write(f"Current working directory: {{current_dir}}")
logger.info(f"Current working directory: {{current_dir}}")

# List files in the current directory
files = os.listdir(current_dir)
st.sidebar.write(f"Files in current directory: {{files}}")
logger.info(f"Files in current directory: {{files}}")
"""

        try:
            return GENERATED_APP_TEMPLATE.format(
                services=service_content,
                debug_content=debug_content
            )
        except KeyError as e:
            self.logger.error(f"Template formatting error: {str(e)}")
            raise ValueError(f"Template formatting error: {str(e)}")

    def _generate_service_content(self, service, params):
        param_dict = json.dumps(params)
        service_name = service.replace('_service', '')
        return f"""
# {service_name.capitalize()} Service
st.header("{service_name.capitalize()} Information")
try:
    logger.info(f"Attempting to get service info for {service_name}")
    service_info = port_manager.get_service_info('{service_name}')
    logger.info(f"Service info for {service_name}: {{service_info}}")
    if not service_info:
        raise ValueError(f"Service info not found for {service_name} service")
    port = service_info['port']
    logger.info(f"Attempting to connect to {service_name.capitalize()} service on port {{port}}")
    params = {param_dict}
    logger.info(f"Sending request with params: {{params}}")
    
    if '{service_name}' == 'restaurant_finder':
        # Ensure the parameters match the RestaurantFinderParams model
        request_params = {{
            'location': params.get('location'),
            'cuisine_type': params.get('cuisine_type'),
            'price_range': params.get('price_range'),
            'dietary_restrictions': params.get('dietary_restrictions'),
            'group_size': params.get('group_size')
        }}
    elif '{service_name}' == 'travel_options':
        # Ensure the parameters match the TravelOptionsParams model
        request_params = {{
            'destination': params.get('destination'),
            'available_time': params.get('available_time'),
            'preferred_mode': params.get('preferred_mode')
        }}
    else:
        request_params = params
    
    # Remove None values
    request_params = {{k: v for k, v in request_params.items() if v is not None}}
    
    response = requests.post(f"http://localhost:{{port}}/{service_name}", json=request_params, timeout=5)
    response.raise_for_status()
    data = response.json()
    render_service_data('{service_name}', data)
    logger.info(f"Successfully connected to {service_name.capitalize()} service and displayed data")
except ValueError as e:
    logger.error(str(e))
    st.error(str(e))
except requests.exceptions.ConnectionError as e:
    logger.error(f"Connection error for {service_name.capitalize()} service: {{e}}")
    st.error(f"Unable to connect to {service_name.capitalize()} service. Please ensure the service is running.")
except requests.exceptions.Timeout as e:
    logger.error(f"Timeout error for {service_name.capitalize()} service: {{e}}")
    st.error(f"Connection to {service_name.capitalize()} service timed out. The service might be overloaded or not responding.")
except requests.exceptions.RequestException as e:
    logger.error(f"Request error for {service_name.capitalize()} service: {{e}}")
    st.error(f"An error occurred while connecting to {service_name.capitalize()} service: {{str(e)}}")
"""

    def _run_app(self, app_file_path, port):
        self.logger.info(f"Running app at {app_file_path} on port {port}")
        subprocess.Popen(
            ["streamlit", "run", app_file_path, "--server.port", str(port)]
        )
