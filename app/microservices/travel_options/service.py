import json
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.microservices.base import MicroserviceBase, UserContext
from datetime import datetime, time

class TravelOptionsParams(BaseModel):
    destination: Optional[List[str]] = None
    available_time: Optional[int] = None
    preferred_mode: Optional[List[str]] = None
    user_id: Optional[str] = None
    max_distance: Optional[float] = None
    accessibility_required: Optional[bool] = None
    budget_per_person: Optional[float] = None
    time_of_day: Optional[str] = None
    weather_preference: Optional[str] = None

class TravelOptionsService(MicroserviceBase):
    def __init__(self):
        super().__init__("travel_options")
        self.update_service_info(
            description="Provides intelligent transportation options and routes to tourist destinations with context-aware recommendations",
            dependencies=[]
        )
        self.travel_options = self.load_travel_options()
        self.popular_times = self.load_popular_times()
        self.route_conditions = self.load_route_conditions()

    def load_travel_options(self):
        try:
            with open('data/travel.txt', 'r') as f:
                return [eval(line) for line in f]
        except FileNotFoundError:
            self.logger.error("travel.txt not found")
            return []
        except Exception as e:
            self.logger.error(f"Error loading travel options: {str(e)}")
            return []

    def load_popular_times(self):
        try:
            with open('data/popular_times.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def load_route_conditions(self):
        try:
            with open('data/route_conditions.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def register_routes(self):
        @self.app.post("/travel_options")
        async def get_travel_options(params: TravelOptionsParams):
            self.logger.info(f"Received parameters: {params}")
            
            # Update user context if user_id is provided
            if params.user_id:
                self.update_user_context(params.user_id, {
                    "time_constraints": {"available_time": params.available_time},
                    "preferences": {
                        "preferred_mode": params.preferred_mode,
                        "weather_preference": params.weather_preference,
                        "time_of_day": params.time_of_day
                    },
                    "accessibility_needs": ["wheelchair_accessible"] if params.accessibility_required else [],
                    "budget_range": {"max": params.budget_per_person} if params.budget_per_person else None
                })
            
            return await self.process_request(params.dict(exclude_unset=True))

    def generate_alternatives(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> List[Dict[str, Any]]:
        alternatives = []
        for rec in recommendations[:2]:  # Generate alternatives for top 2 recommendations
            alt = rec.copy()
            if 'preferred_mode' in alt:
                # Suggest alternative transport modes
                if alt['preferred_mode'] == 'public_transport':
                    alt['preferred_mode'] = 'private_transport'
                    alt['explanation'] = "Faster but more expensive alternative"
                elif alt['preferred_mode'] == 'walk':
                    alt['preferred_mode'] = 'public_transport'
                    alt['explanation'] = "Good balance of cost and convenience"
            alternatives.append(alt)
        return alternatives

    def generate_context_suggestions(self, user_context: UserContext) -> List[Dict[str, Any]]:
        suggestions = []
        if user_context.time_constraints:
            available_time = user_context.time_constraints.get('available_time')
            if available_time and available_time < 120:  # Less than 2 hours
                suggestions.append({
                    "type": "time_management",
                    "suggestion": "Consider nearby attractions to maximize your time",
                    "locations": ["Nearby Park", "Local Market"]
                })
        
        if user_context.budget_range:
            if user_context.budget_range.get('max', float('inf')) < 500:
                suggestions.append({
                    "type": "budget_friendly",
                    "suggestion": "Check out these budget-friendly transport options",
                    "options": ["Public Bus", "Metro", "Shared Rides"]
                })
        
        return suggestions

    def generate_explanation(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> str:
        if not recommendations:
            return "No recommendations found matching your criteria."
        
        explanation = "These recommendations are based on "
        factors = []
        
        if user_context.time_constraints:
            factors.append("your available time")
        if user_context.budget_range:
            factors.append("your budget preferences")
        if user_context.accessibility_needs:
            factors.append("accessibility requirements")
        
        explanation += ", ".join(factors) if factors else "general popularity"
        explanation += ". "
        
        top_rec = recommendations[0]
        explanation += f"The top recommendation is {top_rec.get('destination', 'unknown')} "
        explanation += f"via {top_rec.get('preferred_mode', 'various transport options')}."
        
        return explanation

    def suggest_next_steps(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> List[str]:
        next_steps = []
        if recommendations:
            next_steps.append(f"Book your transport to {recommendations[0].get('destination')}")
            next_steps.append("Check real-time traffic updates before departure")
            if user_context.group_size and user_context.group_size > 1:
                next_steps.append("Consider group booking discounts")
        return next_steps

    async def process_request(self, params):
        self.logger.info(f"Processing request with params: {params}")
        filtered_options = self.travel_options

        user_context = self.get_user_context(params.get('user_id', 'default'))

        if params.get('destination'):
            destinations = params['destination']
            if isinstance(destinations, str):
                destinations = [destinations]
            filtered_options = [opt for opt in filtered_options 
                              if opt['destination'] in destinations]
            self.logger.info(f"After destination filter: {len(filtered_options)} options")

        if params.get('available_time'):
            filtered_options = [opt for opt in filtered_options 
                              if opt['duration'] <= params['available_time']]
            self.logger.info(f"After time filter: {len(filtered_options)} options")

        if params.get('preferred_mode'):
            modes = params['preferred_mode']
            if isinstance(modes, str):
                modes = [modes]
            filtered_options = [opt for opt in filtered_options 
                              if opt['preferred_mode'] in modes]
            self.logger.info(f"After mode filter: {len(filtered_options)} options")

        if params.get('accessibility_required'):
            filtered_options = [opt for opt in filtered_options 
                              if opt.get('wheelchair_accessible', False)]

        if params.get('budget_per_person'):
            filtered_options = [opt for opt in filtered_options 
                              if opt.get('cost_per_person', float('inf')) <= params['budget_per_person']]

        # Enrich options with additional context
        for option in filtered_options:
            option['popular_times'] = self.popular_times.get(option['destination'], {})
            option['route_condition'] = self.route_conditions.get(option['destination'], "normal")
            option['tags'] = option.get('tags', []) + [option['preferred_mode'], option['destination']]

        if not filtered_options:
            self.logger.warning("No travel options found matching the criteria")
            return {
                "recommendations": [],
                "message": "No travel options found matching your criteria."
            }

        # Create base response
        base_response = {
            "recommendations": filtered_options,
            "message": f"Found {len(filtered_options)} travel options matching your criteria."
        }

        # Enrich response with context-aware information
        enriched_response = self.enrich_response(base_response, user_context)
        
        return enriched_response.dict()

def start_travel_options_service():
    service = TravelOptionsService()
    service.run()

if __name__ == "__main__":
    start_travel_options_service()
