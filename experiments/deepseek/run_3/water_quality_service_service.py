import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class WaterQualityRequest(BaseModel):
    locations: Optional[List[str]] = None
    timestamp: Optional[str] = None

class WaterQualityResponse(BaseModel):
    location: str
    timestamp: str
    pH: float
    Dissolved_Oxygen: float
    Conductivity: float
    Turbidity: float
    Temperature: float

class WaterQualityService(MicroserviceBase):
    def __init__(self):
        super().__init__("water_quality_service")
        self.update_service_info(
            description="Service to monitor water quality metrics in different locations.",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/water_quality_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/water_quality_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/water_quality_data.json")
            return []

    def register_routes(self):
        @self.app.post("/water-quality", response_model=List[WaterQualityResponse])
        async def get_water_quality(request: WaterQualityRequest):
            return self.process_request(request)

    def process_request(self, request: WaterQualityRequest):
        results = []
        for entry in self.data:
            if request.locations and entry["location"] not in request.locations:
                continue
            if request.timestamp and entry["timestamp"] != request.timestamp:
                continue
            results.append(WaterQualityResponse(**entry))
        if not results:
            raise HTTPException(status_code=404, detail="No matching data found")
        return results

    def start_water_quality_service():
        service = WaterQualityService()
        service.run()

    if __name__ == "__main__":
        start_water_quality_service()
