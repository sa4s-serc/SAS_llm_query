class HistoricDataService(MicroserviceBase):
    def __init__(self):
        super().__init__("historic_data")
        self.update_service_info(
            description="Provides historical and cultural information about monuments and sites.",
            dependencies=["app.microservices.base.MicroserviceBase"]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/historic_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/historic_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/historic_data.json")
            return []

    @staticmethod
    async def register_routes(app, prefix=''):
        @app.post(prefix + "/search")
        async def search_monument(query: str):
            results = [item for item in self.data if query.lower() in item['name'].lower()]
            return results

    def process_request(self, request):
        pass


def start_historic_data_service():
    service = HistoricDataService()
    service.run()


if __name__ == "__main__":
    start_historic_data_service()
