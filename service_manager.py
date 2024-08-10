class ServiceManager:
    def __init__(self):
        self.services = []
        self.next_port = 5001

    def add_service(self, service_info):
        self.services.append(service_info)

    def find_service(self, query):
        # Simple matching logic - can be made more sophisticated
        query_lower = query.lower()
        for service in self.services:
            if service["service_description"].lower() in query_lower:
                return service
        return None

    def get_next_available_port(self):
        port = self.next_port
        self.next_port += 1
        return port

    def get_services_descriptions(self):
        return [service["service_description"] for service in self.services]
