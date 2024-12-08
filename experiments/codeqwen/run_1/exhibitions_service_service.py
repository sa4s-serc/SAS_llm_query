class ExhibitionsService(MicroserviceBase):
    def __init__(self):
        super().__init__("exhibitions")
        self.update_service_info(
            description="Tracks museum and art exhibitions based on audience type, venue location, exhibition dates, and category.",
            dependencies=["tickets_service"]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/exhibition_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/exhibition_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/exhibition_data.json")
            return []

    @app.post("/search")
    async def search_exhibitions(self, filters: ExhibitionsFilters):
        filtered_exhibitions = [exhibition for exhibition in self.data if all(getattr(exhibition, field) == value for field, value in filters.__dict__.items() if value is not None)]
        return filtered_exhibitions

    @app.post("/add")
    async def add_exhibition(self, exhibition: Exhibition):
        self.data.append(exhibition.dict())
        self.save_data()
        return exhibition

    def save_data(self):
        with open('data/exhibition_data.json', 'w') as f:
            json.dump(self.data, f)

class ExhibitionsFilters(BaseModel):
    interested_audience: Optional[List[str]] = None
    location: Optional[List[str]] = None
    date_range: Optional[List[str]] = None
    exhibition_type: Optional[List[str]] = None

class Exhibition(BaseModel):
    interested_audience: str
    location: str
    date_range: str
    exhibition_type: str

if __name__ == "__main__":
    exhibitions_service = ExhibitionsService()
exhibitions_service.run()
