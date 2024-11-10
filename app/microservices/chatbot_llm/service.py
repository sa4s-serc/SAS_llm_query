from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Tuple
from app.microservices.base import MicroserviceBase
from app.utils.llm_utils import load_microservices, load_summary, load_service_parameters
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import os
from dotenv import load_dotenv

load_dotenv()

class ChatInput(BaseModel):
    user_input: str
    conversation_state: Dict

class ChatbotLLMService(MicroserviceBase):
    def __init__(self):
        super().__init__("chatbot_llm")
        self.update_service_info(
            description="LLM-based chatbot service for IIIT Companion",
            dependencies=[]
        )
        
        # Initialize OpenAI configuration
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            self.logger.error("OpenAI API key not found in environment variables")
            raise ValueError("OpenAI API key not found")
        
        # Use gpt-3.5-turbo as default model
        self.llm = ChatOpenAI(
            api_key=api_key,
            model_name="gpt-4o-mini",  # Explicitly set to gpt-3.5-turbo
            temperature=0.7
        )
        self.logger.info("Successfully initialized ChatOpenAI with gpt-3.5-turbo model")

        # Load service data
        try:
            self.microservices = load_microservices("langchain/services.txt")
            self.system_summary = load_summary("langchain/summary.txt")
            self.params_list = load_service_parameters("langchain/service_params.txt")
            self.logger.info("Successfully loaded service data")
        except Exception as e:
            self.logger.error(f"Error loading service data: {str(e)}")
            raise

    def register_routes(self):
        @self.app.post("/chat")
        async def chat(chat_input: ChatInput):
            try:
                return await self.process_request(chat_input)
            except Exception as e:
                self.logger.error(f"Error in chat endpoint: {str(e)}")
                raise HTTPException(status_code=500, detail=str(e))

    async def process_request(self, chat_input):
        try:
            response, updated_state = self.chatbot_conversation(
                chat_input.user_input,
                chat_input.conversation_state
            )
            return {
                "response": response,
                "conversation_state": updated_state
            }
        except Exception as e:
            self.logger.error(f"Error in chatbot conversation: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    def prepare_system_context(self, microservices: List[Dict[str, str]], system_summary: str, params_list: Dict) -> str:
        params_context = "\n".join([
            f"Service '{service}' options: " + 
            ", ".join([f"{param}: {', '.join(values)}" for param, values in params.items()])
            for service, params in params_list.items()
        ])
        
        return f"""You are an intelligent Hyderabad City Guide designed to help tourists explore the city effectively.
        {system_summary}
        
        Available service options:
        {params_context}
        
        Share information about Hyderabad naturally, suggesting relevant options based on tourist interests.
        Don't mention checking real-time data or making actual reservations.
        Focus on understanding preferences and providing relevant information.
        
        Available services for recommendations:
        {", ".join([ms['name'] for ms in microservices])}
        """

    def identify_services_and_params(
        self,
        conversation: List[str], 
        microservices: List[Dict[str, str]], 
        params_list: Dict,
        llm: ChatOpenAI
    ) -> Tuple[List[str], Dict]:
        params_context = "\n".join([
            f"Service '{service}' options: " + 
            ", ".join([f"{param}: {', '.join(values)}" for param, values in params.items()])
            for service, params in params_list.items()
        ])
        
        identification_prompt = f"""Based ONLY on what has been EXPLICITLY mentioned or agreed to by the user in this conversation, identify:
        1. The relevant services from: {', '.join([ms['name'] for ms in microservices])}
        2. For each service, list ONLY the parameter values that were directly mentioned or confirmed by the user.

        Conversation:
        {' '.join(conversation)}

        Format your response as:
        service_name1:
        - param1: [value1, value2, value3]
        - param2: [value4, value5]

        Guidelines:
        - ONLY include services and parameters that the user explicitly mentioned or confirmed
        - DO NOT include implied or suggested options that weren't confirmed
        - DO NOT include locations or options that were only mentioned by the assistant
        - If a service was mentioned but no specific parameters were confirmed, do not include that service
        - Stick to the available options from this list:
        {params_context}

        Return ONLY the structured list, no explanations."""

        response = llm([HumanMessage(content=identification_prompt)])
        
        services_and_params = {}
        current_service = None
        
        for line in response.content.split('\n'):
            line = line.strip()
            if line and not line.startswith('-'):
                current_service = line.replace(':', '').strip()
                services_and_params[current_service] = {}
            elif line.startswith('-') and current_service:
                param, values = line[1:].split(':', 1)
                values = [v.strip() for v in values.strip()[1:-1].split(',')]
                services_and_params[current_service][param.strip()] = values

        return list(services_and_params.keys()), services_and_params

    def generate_summary(self, conversation: List[str], available_hours: int, llm: ChatOpenAI) -> str:
        summary_prompt = f"""Summarize the tourist's focused plan based on this conversation:
        {' '.join(conversation)}
        
        Include:
        - Main activities they're interested in
        - Their specific preferences and requirements
        - Time allocation within their {available_hours} hour constraint
        
        Start with 'It looks like you're planning to...' and keep it concise and natural.
        Focus on details that will help identify relevant services and parameters."""

        response = llm([HumanMessage(content=summary_prompt)])
        return response.content

    def chatbot_conversation(self, user_input: str, conversation_state: Dict) -> Tuple[str, Dict]:
        try:
            if "system_context" not in conversation_state:
                conversation_state["system_context"] = self.prepare_system_context(
                    self.microservices,
                    self.system_summary,
                    self.params_list
                )
                conversation_state["conversation_history"].append(
                    SystemMessage(content=conversation_state["system_context"])
                )

            # Add user input to conversation history
            conversation_state["conversation_history"].append(HumanMessage(content=user_input))
            conversation_state["exchanges"] += 1

            # If user disagreed with previous suggestion
            if conversation_state.get("awaiting_confirmation", False):
                if "yes" in user_input.lower():
                    conversation_state["ready_for_app"] = True
                    return "Great! I'll create your personalized IIIT Companion app now.", conversation_state
                else:
                    # Store current suggestions before resetting
                    if conversation_state["suggested_services"]:
                        conversation_state["previous_suggestions"].append({
                            "services": conversation_state["suggested_services"],
                            "parameters": conversation_state["parameters"]
                        })
                    
                    # Reset exchanges but keep conversation history
                    conversation_state["exchanges"] = 0
                    conversation_state["awaiting_confirmation"] = False
                    conversation_state["attempt_count"] += 1
                    
                    # Clear current suggestions but keep history
                    conversation_state["suggested_services"] = []
                    conversation_state["parameters"] = {}
                    
                    return "I understand. Let's continue our conversation to better understand your needs. What else would you like to tell me?", conversation_state

            # Generate assistant response
            if conversation_state["exchanges"] == 1:
                prompt = """
                    Start with a warm greeting and introduce yourself as a Hyderabad guide.
                    Ask the visitor about their interests and how much time they have to explore.
                    Keep it natural and friendly.
                """
            else:
                prompt = """
                    As a Hyderabad City Guide, respond naturally to the tourist.
                    Build on the previous conversation.
                    Ask relevant follow-up questions based on their responses.
                    Suggest activities only if enough context is available.
                    Keep the conversation natural and informative.
                """

            # Use invoke instead of direct call and handle the response properly
            messages = conversation_state["conversation_history"] + [HumanMessage(content=prompt)]
            response = self.llm.invoke(messages)
            
            # Handle the response based on its type
            if hasattr(response, 'content'):
                assistant_response = response.content
            elif isinstance(response, dict) and 'content' in response:
                assistant_response = response['content']
            elif isinstance(response, str):
                assistant_response = response
            else:
                self.logger.warning(f"Unexpected response type: {type(response)}")
                assistant_response = str(response)

            conversation_state["conversation_history"].append(AIMessage(content=assistant_response))

            # Check if we have enough exchanges and try to identify services
            if conversation_state["exchanges"] >= conversation_state["max_exchanges"]:
                # Try to identify services and parameters
                services, params = self.identify_services_and_params(
                    [msg.content if hasattr(msg, 'content') else str(msg) for msg in conversation_state["conversation_history"]],
                    self.microservices,
                    self.params_list,
                    self.llm
                )

                # Generate summary
                summary = self.generate_summary(
                    [msg.content if hasattr(msg, 'content') else str(msg) for msg in conversation_state["conversation_history"]],
                    conversation_state["available_hours"],
                    self.llm
                )
                
                # Display current and previous suggestions
                response = f"{summary}\n\nBased on our conversation, I've identified these services and parameters:\n\n"
                
                if services and any(params.values()):
                    conversation_state["suggested_services"] = services
                    conversation_state["parameters"] = params
                    
                    # Display current suggestions
                    for service in services:
                        response += f"📍 {service}:\n"
                        if service in params and params[service]:
                            for param, values in params[service].items():
                                response += f"   • {param}: {', '.join(values)}\n"
                        else:
                            response += "   • No specific parameters identified\n"
                    
                    # Display previous suggestions if any
                    if conversation_state["previous_suggestions"]:
                        response += "\nPrevious suggestions:\n"
                        for idx, prev in enumerate(conversation_state["previous_suggestions"], 1):
                            response += f"\nAttempt {idx}:\n"
                            for service in prev["services"]:
                                response += f"📍 {service}:\n"
                                if service in prev["parameters"] and prev["parameters"][service]:
                                    for param, values in prev["parameters"][service].items():
                                        response += f"   • {param}: {', '.join(values)}\n"
                
                response += "\nDoes this accurately reflect what you're looking for? (Yes/No)"
                conversation_state["awaiting_confirmation"] = True
                return response, conversation_state

            return assistant_response, conversation_state

        except Exception as e:
            self.logger.error(f"Error in chatbot conversation: {str(e)}")
            raise

def start_chatbot_llm_service():
    service = ChatbotLLMService()
    service.run()

if __name__ == "__main__":
    start_chatbot_llm_service() 