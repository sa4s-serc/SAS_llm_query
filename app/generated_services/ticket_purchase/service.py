import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class Ticket(BaseModel):
    Event_Name: str
    Ticket_Price: int

class TicketService(MicroserviceBase):
    def __init__(self):
        super().__init__("ticket_service")
        self.update_service_info(
            description="Service to find available tickets based on event names and price ranges",
            dependencies=[]
        )
        self.data = self.load_data()

    def load_data(self):
        try:
            with open('data/event_ticket_prices.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("data/event_ticket_prices.json not found")
            return []
        except json.JSONDecodeError:
            self.logger.error("Error decoding data/event_ticket_prices.json")
            return []

    def register_routes(self):
        @app.post('/find_tickets/')
        async def find_tickets(event_names: Optional[List[str]] = None, min_price: Optional[int] = None, max_price: Optional[int] = None):
            return self.process_request(event_names, min_price, max_price)

    def process_request(self, event_names: Optional[List[str]], min_price: Optional[int], max_price: Optional[int]):
        result = []
        for entry in self.data:
            if event_names and entry['Event Name'] not in event_names:
                continue
            if (min_price is not None and entry['Ticket Price'] < min_price) or (max_price is not None and entry['Ticket Price'] > max_price):
                continue
            result.append(entry)
        return result

def start_ticket_service():
    app = FastAPI()
    service = TicketService()
    service.register_routes()
    return app

if __name__ == '__main__':
    start_ticket_service()
