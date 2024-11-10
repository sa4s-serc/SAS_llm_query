import requests
from typing import Dict, Tuple
import os
from app.utils.logger import setup_logger

logger = setup_logger("ChatbotClient")

def initialize_conversation() -> Dict:
    """Initialize the conversation state"""
    return {
        "conversation_history": [],
        "microservices": [],
        "system_summary": "",
        "params_list": {},
        "available_hours": 4,
        "exchanges": 0,
        "max_exchanges": 3,
        "suggested_services": [],
        "parameters": {},
        "awaiting_confirmation": False,
        "attempt_count": 1,
        "previous_suggestions": []
    }

def chatbot_conversation(user_input: str, conversation_state: Dict) -> Tuple[str, Dict]:
    """
    Send chat request to the chatbot LLM service and return response
    """
    try:
        # Get the chatbot service port from services.toml
        from app.utils.port_manager import get_port_manager
        port_manager = get_port_manager()
        service_info = port_manager.get_service_info("chatbot_llm")
        
        if not service_info:
            logger.error("Chatbot LLM service info not found")
            return "I'm sorry, but I'm having trouble connecting to the chat service.", conversation_state

        port = service_info["port"]
        
        # Prepare the request
        url = f"http://localhost:{port}/chat"
        payload = {
            "user_input": user_input,
            "conversation_state": conversation_state
        }

        # Send request to chatbot service
        logger.info(f"Sending request to chatbot service: {payload}")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()

        # Process response
        result = response.json()
        logger.info(f"Received response from chatbot service: {result}")

        return result["response"], result["conversation_state"]

    except requests.exceptions.RequestException as e:
        logger.error(f"Error communicating with chatbot service: {str(e)}")
        return "I'm sorry, but I'm having trouble processing your request right now.", conversation_state
    except Exception as e:
        logger.error(f"Unexpected error in chatbot conversation: {str(e)}")
        return "I apologize, but something went wrong. Please try again.", conversation_state
