class ServiceManager:
    def __init__(self):
        self.services = []
        self.next_port = 5001

    def add_service(self, service_info):
        self.services.append(service_info)

    def get_next_available_port(self):
        port = self.next_port
        self.next_port += 1
        return port

    def get_services_descriptions(self):
        return [service["service_description"] for service in self.services]
