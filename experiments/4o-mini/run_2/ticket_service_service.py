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
        @self.app.post("/tickets/available")
        async def find_tickets(event_names: Optional[List[str]] = None, min_price: Optional[int] = None, max_price: Optional[int] = None):
            return self.process_request(event_names, min_price, max_price)

    def process_request(self, event_names: Optional[List[str]], min_price: Optional[int], max_price: Optional[int]):
        available_tickets = []
        for ticket in self.data:
            if (event_names is None or ticket['Event Name'] in event_names) and 
               (min_price is None or ticket['Ticket Price'] >= min_price) and 
               (max_price is None or ticket['Ticket Price'] <= max_price):
                available_tickets.append(ticket)
        return available_tickets


def start_ticket_service():
    service = TicketService()
    service.register_routes()
    service.run()


if __name__ == "__main__":
    start_ticket_service()
