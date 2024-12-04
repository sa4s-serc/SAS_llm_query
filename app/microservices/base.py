from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.utils.port_manager import get_service_port, update_service_info
from app.utils.logger import setup_logger
from datetime import datetime


class UserContext(BaseModel):
    user_preferences: Optional[Dict[str, Any]] = None
    time_constraints: Optional[Dict[str, Any]] = None
    location: Optional[str] = None
    interests: Optional[List[str]] = None
    previous_interactions: Optional[List[Dict[str, Any]]] = None
    accessibility_needs: Optional[List[str]] = None
    group_size: Optional[int] = None
    budget_range: Optional[Dict[str, float]] = None
    special_requirements: Optional[List[str]] = None

class ServiceResponse(BaseModel):
    recommendations: List[Dict[str, Any]]
    context_based_suggestions: Optional[List[Dict[str, Any]]] = None
    alternative_options: Optional[List[Dict[str, Any]]] = None
    relevance_score: Optional[float] = None
    explanation: Optional[str] = None
    next_steps: Optional[List[str]] = None

class MicroserviceBase:
    def __init__(self, name: str):
        self.name = name
        self.port = get_service_port(name)
        self.app = FastAPI()
        self.logger = setup_logger(f"Microservice-{name}")
        self.user_contexts = {}

        self.logger.info(f"Initializing {self.name} microservice on port {self.port}")

    def start(self):
        self.logger.info(f"Starting {self.name} microservice on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

    def register_routes(self):
        # override by child classes
        pass

    def update_service_info(self, description: str, dependencies: list = None):
        if dependencies is None:
            dependencies = []
        update_service_info(self.name, description, dependencies)
        self.logger.info(f"Updated service info for {self.name}")

    def run(self):
        self.register_routes()
        self.start()

    def update_user_context(self, user_id: str, context_data: Dict[str, Any]):
        """Update user context with new information"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = UserContext()
        
        current_context = self.user_contexts[user_id]
        for key, value in context_data.items():
            if hasattr(current_context, key):
                setattr(current_context, key, value)

        self.logger.info(f"Updated context for user {user_id}: {context_data}")

    def get_user_context(self, user_id: str) -> UserContext:
        """Retrieve user context"""
        return self.user_contexts.get(user_id, UserContext())

    def calculate_relevance_score(self, recommendation: Dict[str, Any], user_context: UserContext) -> float:
        """Calculate how relevant a recommendation is based on user context"""
        score = 1.0
        
        if user_context.interests and recommendation.get('tags'):
            matching_interests = len(set(user_context.interests) & set(recommendation['tags']))
            score *= (1 + 0.2 * matching_interests)
        
        if user_context.budget_range and recommendation.get('price'):
            if recommendation['price'] <= user_context.budget_range.get('max', float('inf')) and \
               recommendation['price'] >= user_context.budget_range.get('min', 0):
                score *= 1.2
            else:
                score *= 0.5
        
        if user_context.time_constraints and recommendation.get('duration'):
            if recommendation['duration'] <= user_context.time_constraints.get('available_time', float('inf')):
                score *= 1.2
            else:
                score *= 0.3
        
        return min(score, 2.0)  # Cap the score at 2.0

    def enrich_response(self, base_response: Dict[str, Any], user_context: UserContext) -> ServiceResponse:
        """Enrich the base response with context-based information"""
        recommendations = base_response.get('recommendations', [])
        
        # Calculate relevance scores and sort recommendations
        scored_recommendations = []
        for rec in recommendations:
            score = self.calculate_relevance_score(rec, user_context)
            rec['relevance_score'] = score
            scored_recommendations.append(rec)
        
        scored_recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        # Generate alternative options based on user context
        alternatives = self.generate_alternatives(scored_recommendations, user_context)
        
        # Create enriched response
        return ServiceResponse(
            recommendations=scored_recommendations[:5],  # Top 5 recommendations
            context_based_suggestions=self.generate_context_suggestions(user_context),
            alternative_options=alternatives,
            relevance_score=sum(r['relevance_score'] for r in scored_recommendations[:5]) / 5,
            explanation=self.generate_explanation(scored_recommendations[:5], user_context),
            next_steps=self.suggest_next_steps(scored_recommendations[:5], user_context)
        )

    def generate_alternatives(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> List[Dict[str, Any]]:
        """Generate alternative recommendations based on user context"""
        return []  # Override in specific services

    def generate_context_suggestions(self, user_context: UserContext) -> List[Dict[str, Any]]:
        """Generate additional suggestions based on user context"""
        return []  # Override in specific services

    def generate_explanation(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> str:
        """Generate explanation for recommendations"""
        return "Recommendations based on your preferences and context"

    def suggest_next_steps(self, recommendations: List[Dict[str, Any]], user_context: UserContext) -> List[str]:
        """Suggest next steps based on recommendations"""
        return []  # Override in specific services

    async def process_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # This method should be implemented by child classes
        raise NotImplementedError("This method should be implemented by child classes")
