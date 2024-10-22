import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase

class TicketPurchaseParams(BaseModel):
    ticket_type: str

class TicketPurchaseService(MicroserviceBase):
    def __init__(self):
        super().__init__("ticket_purchase")
        self.update_service_info(
            description="Enables online ticket purchases for attractions and events",
            dependencies=[]
        )
        self.ticket_data = self.load_ticket_data()

    def load_ticket_data(self):
        with open('data/event_ticket_prices.csv', 'r') as f:
            lines = f.readlines()[1:]  # Skip header
            return {line.split(',')[0]: int(line.split(',')[1]) for line in lines}

    def register_routes(self):
        @self.app.post("/ticket_purchase")
        async def purchase_ticket(params: TicketPurchaseParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        ticket_type = params["ticket_type"]
        if ticket_type in self.ticket_data:
            return {
                "ticket_type": ticket_type,
                "price": self.ticket_data[ticket_type],
                "purchase_status": "success"
            }
        else:
            raise HTTPException(status_code=404, detail="Ticket type not found")

def start_ticket_purchase_service():
    service = TicketPurchaseService()
    service.run()

if __name__ == "__main__":
    start_ticket_purchase_service()
