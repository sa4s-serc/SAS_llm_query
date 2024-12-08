class RestaurantRecommendationService(MicroserviceBase):
    def __init__(self):
        super().__init__("restaurant_recommendation")
        self.update_service_info(
            description="This service recommends restaurants based on user preferences.",
            dependencies=[
                Depends(RestaurantDataLoader),
            ]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/restaurant_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/restaurant_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/restaurant_data.json")
            return []

    @router.post("/recommend")
    async def recommend_restaurants(self, params: RecommendationParams):
        filtered_restaurants = [restaurant for restaurant in self.data if all(getattr(params, key, None) == getattr(restaurant, key, None) for key in params.__fields__)]
        return filtered_restaurants

    @router.post("/validate")
    async def validate_preferences(self, params: RecommendationParams):
        errors = {}
        for field in params.__fields__:
            if getattr(params, field, None) is None:
                errors[field] = "Required"
        if errors:
            raise HTTPException(status_code=400, detail=errors)
        return True

class RecommendationParams(BaseModel):
    location: Optional[str] = None
    cuisine_type: Optional[str] = None
    price_range: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    group_size: Optional[int] = None

class RestaurantDataLoader(BaseModel):
    pass
