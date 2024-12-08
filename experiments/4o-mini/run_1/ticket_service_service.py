import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase


class TicketData(BaseModel):
    Event_Name: str
    Ticket_Price: int


class TicketService(MicroserviceBase):
    def __init__(self):
        super().__init__("ticket_service")
        self.update_service_info(
            description="Service to find available tickets based on event names and price ranges.",
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

    def process_request(self, event_names: Optional[List[str]], price_range: Optional[List[int]]):
        filtered_tickets = []
        for ticket in self.data:
            event_name = ticket.get('Event Name')
            ticket_price = ticket.get('Ticket Price')
            if event_names and event_name not in event_names:
                continue
            if price_range and not (price_range[0] <= ticket_price <= price_range[1]):
                continue
            filtered_tickets.append(ticket)
        return filtered_tickets

    def register_routes(self):
        @self.app.post("/find_tickets")
        async def find_tickets(event_names: Optional[List[str]] = None, price_range: Optional[List[int]] = None):
            result = self.process_request(event_names, price_range)
            if not result:
                raise HTTPException(status_code=404, detail="No tickets found matching the criteria")
            return result


def start_ticket_service():
    service = TicketService()
    service.run()


if __name__ == "__main__":
    start_ticket_service()
