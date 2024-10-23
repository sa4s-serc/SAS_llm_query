import csv
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
from app.microservices.base import MicroserviceBase

class TicketPurchaseParams(BaseModel):
    event_name: str

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
            reader = csv.DictReader(f)
            return {row['Event Name']: int(row['Ticket Price']) for row in reader}

    def register_routes(self):
        @self.app.post("/ticket_purchase")
        async def purchase_ticket(params: TicketPurchaseParams):
            return await self.process_request(params.dict())

    async def process_request(self, params):
        event_name = params['event_name']
        if event_name in self.ticket_data:
            return {
                "event_name": event_name,
                "ticket_price": self.ticket_data[event_name],
                "purchase_status": "success"
            }
        else:
            raise HTTPException(status_code=404, detail="Event not found")

def start_ticket_purchase_service():
    service = TicketPurchaseService()
    service.run()

if __name__ == "__main__":
    start_ticket_purchase_service()
