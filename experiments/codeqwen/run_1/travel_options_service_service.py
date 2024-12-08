class TravelOptionsService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_options")
        self.update_service_info(
            description="Provides travel options based on destination, available time, and preferred mode of transport.",
            dependencies=["database", "cache"],
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/travel.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/travel.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/travel.json")
            return []

    @staticmethod
    def validate_request_body(data: dict):
        required_fields = {"destination", "available_time", "preferred_mode"}
        if not required_fields.issubset(data.keys()):
            raise HTTPException(status_code=400, detail="Missing required fields")
        if not isinstance(data["available_time"], int):
            raise HTTPException(status_code=400, detail="Invalid type for available_time")
        if data["preferred_mode"] not in ['car', 'bus', 'train']:
            raise HTTPException(status_code=400, detail="Invalid preferred_mode")

    def process_request(self, data: dict):
        TravelOptionsService.validate_request_body(data)
        filtered_data = [item for item in self.data if item["destination"] == data["destination"] and item["available_time"] >= data["available_time"] and item["preferred_mode"] == data["preferred_mode"]]
        return filtered_data

    def register_routes(self):
        @self.app.post("/search")
        async def search(request_data: dict):
            result = self.process_request(request_data)
            return result

if __name__ == "__main__":
    service = TravelOptionsService()
    service.run()
