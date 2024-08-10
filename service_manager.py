class ServiceManager:
    def __init__(self):
        self.services = []
        self.next_port = 5001
        self.databases = [
            {
                "name": "temperature_db",
                "path": "temperature_data.db",
                "description": "This database stores hourly temperature readings. Each record contains an ID, a timestamp, and a temperature value in Celsius.",
                "schema": {
                    "temperature_readings": {
                        "columns": [
                            {"name": "id", "type": "INTEGER", "primary_key": True},
                            {"name": "timestamp", "type": "DATETIME"},
                            {"name": "temperature", "type": "FLOAT"},
                        ]
                    }
                },
            }
        ]

    def add_service(self, service_info):
        self.services.append(service_info)

    def get_next_available_port(self):
        port = self.next_port
        self.next_port += 1
        return port

    def get_services_descriptions(self):
        return [service["service_description"] for service in self.services]

    def get_database_info(self):
        return self.databases

    def add_database(self, database_info):
        if "description" not in database_info:
            raise ValueError("Database info must include a description")
        self.databases.append(database_info)

    def get_database_by_name(self, name):
        for db in self.databases:
            if db["name"] == name:
                return db
        return None

    def update_database_description(self, name, new_description):
        db = self.get_database_by_name(name)
        if db:
            db["description"] = new_description
            return True
        return False
