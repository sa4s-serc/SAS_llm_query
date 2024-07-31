import os
import multiprocessing
import signal
import time
from flask import Flask, request, jsonify

VENV_PATH = "/home/bassam/Documents/research/code/venv/bin/activate"
SERVICES_PATH = "/home/bassam/Documents/research/code/services"


def run_service(filename, port):
    os.system(f"source {VENV_PATH} && python {filename}")


class ServiceManager:
    def __init__(self):
        self.services = {}
        self.next_port = 5001

        if not os.path.exists(SERVICES_PATH):
            os.makedirs(SERVICES_PATH)

    def get_services(self):
        return self.services

    def create_service(self, service_code, query_type):
        port = self.next_port
        self.next_port += 1
        print("CODE RECEIVED \n\n\n", service_code, "\n\n\n\n")

        # Replace {port} placeholder and unescape newline characters
        service_code = service_code.replace("{port}", str(port))
        service_code = service_code.replace("\\n", "\n")

        # Replace any remaining hardcoded port references
        service_code = service_code.replace("port=5000", f"port={port}")

        # Create a unique filename for this service
        filename = os.path.join(SERVICES_PATH, f"service_{query_type}_{port}.py")
        with open(filename, "w") as f:
            f.write(service_code)

        # Start the service in a new process
        process = multiprocessing.Process(target=run_service, args=(filename, port))
        process.start()

        # Wait a bit to ensure the service has started
        time.sleep(2)

        self.services[query_type] = {
            "port": port,
            "process": process,
            "filename": filename,
        }

        return f"http://localhost:{port}"

    def stop_service(self, query_type):
        if query_type in self.services:
            service = self.services[query_type]
            if service["process"].is_alive():
                os.kill(service["process"].pid, signal.SIGTERM)
                service["process"].join(timeout=5)
                if service["process"].is_alive():
                    os.kill(service["process"].pid, signal.SIGKILL)

            # Remove the service file
            if os.path.exists(service["filename"]):
                os.remove(service["filename"])

            del self.services[query_type]

    def cleanup(self):
        for service in self.services.values():
            if service["process"].is_alive():
                os.kill(service["process"].pid, signal.SIGTERM)
                service["process"].join(timeout=5)
                if service["process"].is_alive():
                    os.kill(service["process"].pid, signal.SIGKILL)

            # Remove the service file
            if os.path.exists(service["filename"]):
                os.remove(service["filename"])

        self.services.clear()

    def get_service(self, query_type):
        return self.services.get(query_type)

    def service_exists(self, query_type):
        return query_type in self.services
