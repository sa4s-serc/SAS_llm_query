import os
import json
import streamlit as st
from typing import Dict, List
import subprocess
import signal
import psutil
import sys
import importlib
import threading
import time
from app.utils.logger import setup_logger
from app.utils.port_manager import PortManager

logger = setup_logger("ServiceManager")
port_manager = PortManager()

class ServiceManager:
    def __init__(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.app_dir = os.path.join(self.project_root, "app")
        self.services_state_file = os.path.join(self.project_root, "data", "services_state.json")
        self.services_dir = os.path.join(self.app_dir, "microservices")
        self.python_executable = sys.executable
        self.ensure_state_file_exists()
        self.process_map = {}
        self.port_manager = PortManager()
        
        # Add project root to Python path
        if self.project_root not in sys.path:
            sys.path.insert(0, self.project_root)
        
        logger.info(f"Using Python executable: {self.python_executable}")
        logger.info(f"Project root: {self.project_root}")
        logger.info(f"App directory: {self.app_dir}")
        logger.info(f"Services directory: {self.services_dir}")

    def ensure_state_file_exists(self):
        """Create services state file if it doesn't exist"""
        data_dir = os.path.dirname(self.services_state_file)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        if not os.path.exists(self.services_state_file):
            initial_state = {
                service: {"enabled": False, "pid": None} 
                for service in self.get_available_services()
            }
            with open(self.services_state_file, "w") as f:
                json.dump(initial_state, f, indent=4)

    def get_available_services(self) -> List[str]:
        """Get list of available services from microservices directory"""
        services = {}
        for item in os.listdir(self.services_dir):
            if os.path.isdir(os.path.join(self.services_dir, item)) and not item.startswith('__'):
                service_file = os.path.join(self.services_dir, item, "service.py")
                if os.path.exists(service_file):
                    module_name = f"app.microservices.{item}.service"
                    services[item] = module_name
        return sorted(services.keys())

    def get_service_states(self) -> Dict:
        """Get current state of all services"""
        try:
            with open(self.services_state_file, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading service states: {e}")
            return {}

    def save_service_states(self, states: Dict):
        """Save service states to file"""
        try:
            with open(self.services_state_file, "w") as f:
                json.dump(states, f, indent=4)
        except Exception as e:
            logger.error(f"Error saving service states: {e}")

    def check_dependency_health(self, dependency: str) -> bool:
        """Check if a dependency service is healthy"""
        service_info = self.port_manager.get_service_info(dependency)
        if not service_info:
            logger.error(f"Service info not found for dependency: {dependency}")
            return False
        port = service_info["port"]
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def run_microservice(self, module_name: str, service_name: str):
        """Run a single microservice"""
        try:
            # Check if service is already running
            if self.check_service_status(service_name):
                logger.info(f"Service {service_name} is already running")
                return
            
            logger.info(f"Importing module {module_name} for {service_name}")
            module = importlib.import_module(module_name)
            
            logger.info(f"Getting start function for {service_name}")
            start_function = getattr(module, f"start_{service_name.lower()}_service")
            
            logger.info(f"Starting {service_name} service")
            start_function()
            
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {str(e)}")
            # Update state to indicate service failed to start
            states = self.get_service_states()
            if service_name in states:
                states[service_name]["enabled"] = False
                states[service_name]["pid"] = None
                self.save_service_states(states)
            raise

    def toggle_service(self, service_name: str, enable: bool):
        """Toggle a service on or off"""
        states = self.get_service_states()
        
        if service_name not in states:
            states[service_name] = {"enabled": enable, "pid": None}
        else:
            states[service_name]["enabled"] = enable

        if enable:
            self._start_service(service_name)
        else:
            self._stop_service(service_name)

        self.save_service_states(states)
        return states[service_name]["enabled"]

    def _start_service(self, service_name: str):
        """Start a service"""
        try:
            # Check dependencies first
            service_info = self.port_manager.get_service_info(service_name)
            if service_info and "dependencies" in service_info:
                for dependency in service_info["dependencies"]:
                    if not self.check_dependency_health(dependency):
                        logger.error(f"Dependency {dependency} not healthy for {service_name}")
                        return

            # Get module name and create the command
            module_name = f"app.microservices.{service_name}.service"
            
            # Set up Python path to include the project root
            env = os.environ.copy()
            env["PYTHONPATH"] = self.project_root
            
            logger.info(f"Starting service {service_name} with:")
            logger.info(f"Python executable: {self.python_executable}")
            logger.info(f"Project root: {self.project_root}")
            logger.info(f"PYTHONPATH: {env['PYTHONPATH']}")
            logger.info(f"Module to import: {module_name}")
            
            # Create the startup script
            startup_script = f"""
import os
import sys

print("Python path:", os.environ.get('PYTHONPATH'))
print("Sys path:", sys.path)

try:
    print("Attempting to import {module_name}")
    import {module_name}
    print("Successfully imported {module_name}")
    print("Starting service...")
    {module_name}.start_{service_name.lower()}_service()
except Exception as e:
    import traceback
    sys.stderr.write(f"Error starting service: {{str(e)}}\\n")
    sys.stderr.write(traceback.format_exc())
    sys.exit(1)
"""
            
            # Create a temporary file for the startup script
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(startup_script)
                startup_script_path = f.name
            
            logger.info(f"Created startup script at: {startup_script_path}")
            
            try:
                # Start service in a new process group
                process = subprocess.Popen(
                    [self.python_executable, startup_script_path],
                    env=env,
                    start_new_session=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
                
                # Wait a bit for the service to start
                time.sleep(2)
                
                # Check if process is still running
                if process.poll() is None:
                    # Update state
                    states = self.get_service_states()
                    states[service_name]["enabled"] = True
                    states[service_name]["pid"] = process.pid
                    self.save_service_states(states)
                    logger.info(f"Started {service_name} service with PID {process.pid}")
                else:
                    # Process failed to start, get output
                    stdout, stderr = process.communicate()
                    error_msg = f"Service {service_name} failed to start.\nStdout:\n{stdout}\nStderr:\n{stderr}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(startup_script_path)
                except:
                    pass
            
        except Exception as e:
            logger.error(f"Error starting service {service_name}: {str(e)}")
            raise

    def _stop_service(self, service_name: str):
        """Stop a service"""
        try:
            # Get service port and state
            service_info = self.port_manager.get_service_info(service_name)
            if not service_info:
                logger.error(f"No port info found for {service_name}")
                return
            
            port = service_info["port"]
            states = self.get_service_states()
            service_state = states.get(service_name, {})
            service_pid = service_state.get("pid")
            
            logger.info(f"Attempting to stop {service_name} on port {port}")
            service_stopped = False
            
            # First try: Stop by PID if we have it
            if service_pid:
                try:
                    # Try to kill the entire process group
                    pgid = os.getpgid(service_pid)
                    os.killpg(pgid, signal.SIGTERM)
                    
                    # Wait for a bit to see if it terminates
                    try:
                        os.waitpid(service_pid, os.WNOHANG)
                        time.sleep(2)
                        # Check if process is still running
                        os.kill(service_pid, 0)
                        # If we get here, process is still running, send SIGKILL
                        os.killpg(pgid, signal.SIGKILL)
                    except OSError:
                        # Process is already gone
                        pass
                    
                    service_stopped = True
                    logger.info(f"Stopped service {service_name} with PID {service_pid}")
                except ProcessLookupError:
                    logger.debug(f"Process {service_pid} not found")
                except Exception as e:
                    logger.debug(f"Error stopping process {service_pid}: {str(e)}")
            
            # Second try: Find by port if PID method failed
            if not service_stopped:
                try:
                    import subprocess
                    # Find PID using port
                    result = subprocess.run(['lsof', '-ti', f':{port}'], capture_output=True, text=True)
                    if result.stdout.strip():
                        pids = result.stdout.strip().split('\n')
                        for pid_str in pids:
                            try:
                                pid = int(pid_str)
                                pgid = os.getpgid(pid)
                                os.killpg(pgid, signal.SIGTERM)
                                time.sleep(2)
                                try:
                                    os.kill(pid, 0)
                                    os.killpg(pgid, signal.SIGKILL)
                                except OSError:
                                    pass
                                service_stopped = True
                                logger.info(f"Stopped process using port {port}")
                            except (ValueError, ProcessLookupError):
                                continue
                except (subprocess.SubprocessError, FileNotFoundError):
                    logger.debug("lsof command failed or not available")
            
            # Update state
            states[service_name]["enabled"] = False
            states[service_name]["pid"] = None
            self.save_service_states(states)
            logger.info(f"Updated state for {service_name} to stopped")
            
        except Exception as e:
            logger.error(f"Error stopping service {service_name}: {str(e)}")
            raise

    def check_service_status(self, service_name: str) -> bool:
        """Check if a service is actually running"""
        try:
            service_info = self.port_manager.get_service_info(service_name)
            if not service_info:
                return False
            
            port = service_info["port"]
            
            # Check if any process is using this port
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    connections = proc.connections()
                    for conn in connections:
                        if hasattr(conn, 'laddr') and hasattr(conn.laddr, 'port') and conn.laddr.port == port:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    continue
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking service status: {str(e)}")
            return False

    def start_all_services(self):
        """Start all services in the correct order"""
        try:
            services = {}
            for service in self.get_available_services():
                module_name = f"app.microservices.{service}.service"
                services[service] = module_name

            # Start services without dependencies first
            for service_name, module_name in list(services.items()):
                service_info = self.port_manager.get_service_info(service_name)
                if not service_info or "dependencies" not in service_info or not service_info["dependencies"]:
                    self._start_service(service_name)
                    del services[service_name]
                    time.sleep(1)

            # Start services with dependencies
            while services:
                for service_name, module_name in list(services.items()):
                    self._start_service(service_name)
                    del services[service_name]
                    time.sleep(1)

            return True
        except Exception as e:
            logger.error(f"Error starting all services: {str(e)}")
            return False

def render_service_manager():
    """Render the service manager interface"""
    st.title("Service Command Center")
    
    # Initialize the service manager in session state if it doesn't exist
    if 'manager' not in st.session_state:
        st.session_state.manager = ServiceManager()
    
    manager = st.session_state.manager
    services = manager.get_available_services()
    states = manager.get_service_states()

    # Add Start All Services button at the top
    if st.button("🚀 Start All Services", help="Start all services in the correct order"):
        with st.spinner("Starting all services..."):
            if manager.start_all_services():
                st.success("All services started!")
            else:
                st.error("Error starting all services")

    st.markdown("---")
    st.markdown("### Individual Service Controls")
    
    # Create three columns for service groups
    cols = st.columns(3)
    
    # Initialize toggle states in session state if they don't exist
    if 'toggle_states' not in st.session_state:
        st.session_state.toggle_states = {}
    
    for idx, service in enumerate(services):
        with cols[idx % 3]:
            # Get current state
            is_running = manager.check_service_status(service)
            
            # Initialize or update toggle state
            if service not in st.session_state.toggle_states:
                st.session_state.toggle_states[service] = is_running
            
            # Service container
            with st.container():
                st.markdown(f"#### {service.replace('_', ' ').title()}")
                
                # Status and toggle in the same line
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    status = "🟢 Running" if is_running else "🔴 Stopped"
                    st.markdown(f"**Status:** {status}")
                
                with col2:
                    # Use a button instead of a toggle to avoid rerun loops
                    button_label = "Stop" if is_running else "Start"
                    if st.button(button_label, key=f"button_{service}"):
                        with st.spinner(f"{'Stopping' if is_running else 'Starting'} {service}..."):
                            manager.toggle_service(service, not is_running)
                            st.session_state.toggle_states[service] = not is_running
                            time.sleep(1)  # Give the service time to start/stop
                            st.rerun()  # Use st.rerun() instead of experimental_rerun()

if __name__ == "__main__":
    render_service_manager() 