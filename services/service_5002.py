import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import logging

# Base service class, assume MicroserviceBase is defined elsewhere
class MicroserviceBase:
    def __init__(self, service_name: str):
        self.app = FastAPI()
        self.logger = logging.getLogger(service_name)

class MonumentInfoService(MicroserviceBase):
    def __init__(self):
        super().__init__("monument_info_service")
        self.update_service_info(
            description="Service to provide historical and cultural information about monuments and sites.",
            dependencies=[]
        )
        self.data = self.load_data()
        self.register_routes()

    def update_service_info(self, description: str, dependencies: List[str]):
        self.description = description
        self.dependencies = dependencies

    def load_data(self):
        try:
            with open('data/specific_data.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("specific_data.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding specific_data.json")
            return []

    def register_routes(self):
        @self.app.get("/monuments")
        async def get_monuments(site_names: Optional[List[str]] = None):
            self.logger.info(f"Received parameters: {site_names}")
            return await self.process_request(site_names)

    async def process_request(self, site_names):
        self.logger.info(f"Processing request with params: {site_names}")
        filtered_data = self.data

        if site_names:
            if isinstance(site_names, str):
                site_names = [site_names]
            filtered_data = [d for d in filtered_data if d['name'] in site_names]
            self.logger.info(f"After filter: {len(filtered_data)} items")

        if not filtered_data:
            return {"items": [], "message": "No items found matching criteria"}

        return {"items": filtered_data, "message": f"Found {len(filtered_data)} matching items"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(MonumentInfoService().app, host='0.0.0.0', port=5002)
