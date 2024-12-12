import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class TicketRequest(BaseModel):
    event_names: Optional[List[str]] = None
    price_ranges: Optional[List[List[int]]] = None

class TicketResponse(BaseModel):
    event_name: str
    ticket_price: int
    available: bool

class TicketService(MicroserviceBase):
    def __init__(self):
        super().__init__("ticket_service")
        self.update_service_info(
            description="Service to help users find available tickets based on event names and price ranges.",
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
        @self.app.post("/find_tickets", response_model=List[TicketResponse])
        async def find_tickets(request: TicketRequest):
            return self.process_request(request)

    def process_request(self, request: TicketRequest):
        results = []
        for event in self.data:
            event_name = event["Event Name"]
            ticket_price = event["Ticket Price"]
            available = False
            if request.event_names and event_name in request.event_names:
                if request.price_ranges:
                    for price_range in request.price_ranges:
                        if len(price_range) == 2 and price_range[0] <= ticket_price <= price_range[1]:
                            available = True
                            break
                else:
                    available = True
            results.append({
                "event_name": event_name,
                "ticket_price": ticket_price,
                "available": available
            })
        return results

    def start_ticket_service():
        service = TicketService()
        service.run()

    if __name__ == "__main__":
        start_ticket_service()
