class ServiceManager:
    def __init__(self):
        self.services = []
        self.next_port = 5001
        self.json_data_sources = [
            {
                "name": "air_quality_data",
                "path": "data/air_quality_data.json",
                "description": "Contains air quality measurements including AQI, PM2.5, PM10, NO2, and O3 levels for different locations.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "AQI": {"type": "number"},
                            "PM2.5": {"type": "number"},
                            "PM10": {"type": "number"},
                            "NO2": {"type": "number"},
                            "O3": {"type": "number"}
                        }
                    }
                }
            },
            {
                "name": "exhibition_data",
                "path": "data/exhibition_data.json",
                "description": "Contains information about ongoing and upcoming exhibitions including audience type, location, dates, and exhibition type.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "interested_audience": {"type": "string"},
                            "location": {"type": "string"},
                            "date_range": {"type": "string"},
                            "exhibition_type": {"type": "string"}
                        }
                    }
                }
            },
            {
                "name": "crowd_data",
                "path": "data/crowd_quality_data.json",
                "description": "Contains real-time crowd density information for various locations.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "crowd_count": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "name": "event_data",
                "path": "data/event_notifier.json",
                "description": "Contains information about upcoming events, shows, and festivals.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "event": {"type": "string"},
                            "time_required": {"type": "string"},
                            "details": {"type": "string"}
                        }
                    }
                }
            },
            {
                "name": "ticket_data",
                "path": "data/event_ticket_prices.json",
                "description": "Contains event ticket pricing information.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "Event Name": {"type": "string"},
                            "Ticket Price": {"type": "integer"}
                        }
                    }
                }
            },
            {
                "name": "travel_data",
                "path": "data/travel.json",
                "description": "Contains transportation options and routes to tourist destinations.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "destination": {"type": "string"},
                            "available_time": {"type": "integer"},
                            "preferred_mode": {"type": "string"}
                        }
                    }
                }
            },
            {
                "name": "water_quality_data",
                "path": "data/water_quality_data.json",
                "description": "Contains water quality measurements for various water bodies.",
                "schema": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"},
                            "timestamp": {"type": "string", "format": "date-time"},
                            "pH": {"type": "number"},
                            "Dissolved_Oxygen": {"type": "number"},
                            "Conductivity": {"type": "number"},
                            "Turbidity": {"type": "number"},
                            "Temperature": {"type": "number"}
                        }
                    }
                }
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

    def get_json_data_sources(self):
        return self.json_data_sources

    def get_data_source_by_name(self, name):
        for source in self.json_data_sources:
            if source["name"] == name:
                return source
        return None

    def add_json_data_source(self, data_source_info):
        if "description" not in data_source_info or "schema" not in data_source_info:
            raise ValueError("Data source info must include description and schema")
        self.json_data_sources.append(data_source_info)

    def update_data_source_description(self, name, new_description):
        source = self.get_data_source_by_name(name)
        if source:
            source["description"] = new_description
            return True
        return False