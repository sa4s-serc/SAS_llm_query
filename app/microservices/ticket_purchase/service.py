import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.microservices.base import MicroserviceBase

class TicketPurchaseParams(BaseModel):
    event_name: Optional[List[str]] = None
    price_range: Optional[List[int]] = None

class TicketPurchaseService(MicroserviceBase):
    def __init__(self):
        super().__init__("ticket_purchase")
        self.update_service_info(
            description="Enables online ticket purchases for attractions and events",
            dependencies=[]
        )
        self.ticket_data = self.load_ticket_data()

    def load_ticket_data(self):
        try:
            with open('data/event_ticket_prices.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("event_ticket_prices.json not found")
            return {}
        except json.JSONDecodeError:
            self.logger.error("Error decoding event_ticket_prices.json")
            return {}

    def register_routes(self):
        @self.app.post("/ticket_purchase")
        async def purchase_ticket(params: TicketPurchaseParams):
            self.logger.info(f"Received parameters: {params}")
            return await self.process_request(params.dict(exclude_unset=True))

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        available_tickets = []

        if params.get('event_name'):
            event_names = params['event_name']
            if isinstance(event_names, str):
                event_names = [event_names]
            
            for event in event_names:
                if event in self.ticket_data:
                    price = self.ticket_data[event]["price"]
                    if not params.get('price_range') or price in params['price_range']:
                        available_tickets.append({
                            "event_name": event,
                            "ticket_price": price,
                            "purchase_status": "available",
                            "venue": self.ticket_data[event].get("venue", "TBD"),
                            "date": self.ticket_data[event].get("date", "TBD")
                        })
                        self.logger.info(f"Found tickets for event: {event}")
                else:
                    self.logger.warning(f"No tickets found for event: {event}")

        elif params.get('price_range'):
            price_range = params['price_range']
            if isinstance(price_range[0], str):
                price_range = [int(p) for p in price_range]
            
            for event, details in self.ticket_data.items():
                price = details["price"]
                if price in price_range:
                    available_tickets.append({
                        "event_name": event,
                        "ticket_price": price,
                        "purchase_status": "available",
                        "venue": details.get("venue", "TBD"),
                        "date": details.get("date", "TBD")
                    })

        if not available_tickets:
            self.logger.warning("No tickets found matching the criteria")
            return {
                "tickets": [],
                "message": "No tickets found matching your criteria."
            }

        self.logger.info(f"Returning {len(available_tickets)} ticket options")
        return {
            "tickets": available_tickets,
            "message": f"Found {len(available_tickets)} ticket options matching your criteria."
        }

def start_ticket_purchase_service():
    service = TicketPurchaseService()
    service.run()

if __name__ == "__main__":
    start_ticket_purchase_service()
