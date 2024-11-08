import streamlit as st
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import toml
from typing import List, Dict, Tuple
from langchain.schema import HumanMessage, SystemMessage
from app.utils.llm_utils import load_microservices, load_summary, load_service_parameters

load_dotenv()

services_file = os.path.join(os.path.dirname(__file__), "..", "services.toml")
services_config = toml.load(services_file)

available_keywords = [
    service_name.replace("_service", "")
    for service_name in services_config.keys()
    if not service_name.startswith("sensor_")
]

open_ai_key = os.getenv("OPENAI_API_KEY")
open_ai_model = os.getenv("OPEN_AI_MODEL")
llm = ChatOpenAI(openai_api_key=open_ai_key, temperature=0.7, model=open_ai_model)

SERVICE_CONTEXT = """
Locations: Lumbini Park, Hussain Sagar Lake, KBR National Park, Durgam Cheruvu Lake, Ananthagiri Hills, Botanical Gardens, Charminar, Golconda Fort, Mecca Masjid, Chowmahalla Palace, Qutb Shahi Tombs, Salar Jung Museum, Laad Bazaar, HITEC City, GVK One Mall

Exhibition Types: Home Decor Exhibition, Fashion Show, Cosmetics Expo, Music Festival, Textile Fair, Craft Beer Festival, Wellness Expo, Antique Fair, Handicrafts Fair, Shoe Exhibition, Gardening Show, Vintage Collectibles Show

Restaurant Parameters:
- Cuisine Types: Indian, Chinese, Italian, Mexican, Continental, Thai, Fast Food, Vegetarian, Vegan
- Price Ranges: 500, 750, 1000, 1300, 2500
- Dietary Restrictions: None, Vegetarian, Vegan, Gluten-Free, Nut-Free
- Group Sizes: 1, 2, 4, 6, 8, 10

Travel Options:
- Preferred Modes: walk, public_transport, private_transport
- Time Ranges:
  - walk: 5 to 30 minutes
  - public_transport: 10 to 60 minutes
  - private_transport: 5 to 40 minutes

Water Quality Parameters: pH (6.5 to 8.5), Dissolved Oxygen (5 to 12 mg/L), Conductivity (500 to 1500 µS/cm), Turbidity (1 to 10 NTU), Temperature (15 to 35 °C)

Exhibition Parameters:
- Interested Audiences: Art Lovers, Fashion Enthusiasts, Foodies, Collectors, Tech Buffs
"""

def create_conversation_chain(template):
    prompt = PromptTemplate(
        input_variables=["history", "input", "user_context"],
        template=template
    )
    memory = ConversationBufferMemory(input_key="input", memory_key="history")
    return LLMChain(llm=llm, prompt=prompt, memory=memory, verbose=True)


def chatbot_conversation(user_input: str, conversation_state: Dict) -> Tuple[str, Dict]:
    if "system_context" not in conversation_state:
        conversation_state["system_context"] = prepare_system_context(
            conversation_state["microservices"],
            conversation_state["system_summary"],
            conversation_state["params_list"]
        )
        conversation_state["conversation_history"].append(SystemMessage(content=conversation_state["system_context"]))

    # Add user input to conversation history
    conversation_state["conversation_history"].append(HumanMessage(content=user_input))
    conversation_state["exchanges"] += 1

    # If user disagreed with previous suggestion
    if conversation_state.get("awaiting_confirmation", False):
        if "yes" in user_input.lower():
            conversation_state["ready_for_app"] = True
            return "Great! I'll create your personalized IIIT Companion app now.", conversation_state
        else:
            conversation_state["exchanges"] = max(0, conversation_state["exchanges"] - 2)
            conversation_state["awaiting_confirmation"] = False
            return "I understand. Let's continue our conversation to better understand your needs. What else would you like to tell me?", conversation_state

    # Generate assistant response
    if conversation_state["exchanges"] == 1:
        assistant_messages = conversation_state["conversation_history"] + [HumanMessage(content="""
            Start with a warm greeting and introduce yourself as a Hyderabad guide.
            Ask the visitor about their interests and how much time they have to explore.
            Keep it natural and friendly.
        """)]
    else:
        assistant_messages = conversation_state["conversation_history"] + [HumanMessage(content=f"""
            As a Hyderabad City Guide, respond naturally to the tourist.
            Build on the previous conversation.
            Ask relevant follow-up questions based on their responses.
            Suggest activities only if enough context is available.
            Keep the conversation natural and informative.
        """)]

    assistant_response = llm(assistant_messages)
    conversation_state["conversation_history"].append(assistant_response)

    # Check if we have enough exchanges and try to identify services
    if conversation_state["exchanges"] >= 2:
        # Try to identify services and parameters
        services, params = identify_services_and_params(
            [msg.content for msg in conversation_state["conversation_history"]],
            conversation_state["microservices"],
            conversation_state["params_list"],
            llm
        )

        # Only proceed if we have identified services and parameters
        if services and any(params.values()):
            conversation_state["suggested_services"] = services
            conversation_state["parameters"] = params

            # If we have enough exchanges or have gathered sufficient information
            if conversation_state["exchanges"] >= conversation_state["max_exchanges"]:
                # Generate summary
                summary = generate_summary(
                    [msg.content for msg in conversation_state["conversation_history"]],
                    conversation_state["available_hours"],
                    llm
                )
                
                # Display identified services and parameters
                response = f"{summary}\n\nBased on our conversation, I've identified these services and parameters:\n\n"
                for service in services:
                    response += f"📍 {service}:\n"
                    if service in params and params[service]:
                        for param, values in params[service].items():
                            response += f"   • {param}: {', '.join(values)}\n"
                    else:
                        response += "   • No specific parameters identified\n"
                
                response += "\nDoes this accurately reflect what you're looking for? (Yes/No)"
                conversation_state["awaiting_confirmation"] = True
                return response, conversation_state
            else:
                # Continue conversation to gather more details
                return assistant_response.content, conversation_state
        elif conversation_state["exchanges"] >= conversation_state["max_exchanges"]:
            # If we've reached max exchanges but haven't identified services
            return "I need more specific information about what you're interested in. Could you tell me more about what you'd like to do or see in Hyderabad?", conversation_state

    return assistant_response.content, conversation_state

def initialize_conversation():
    return {
        "conversation_history": [],
        "microservices": load_microservices(MICROSERVICES_FILE),
        "system_summary": load_summary(SUMMARY_FILE),
        "params_list": load_service_parameters(PARAMS_FILE),
        "available_hours": 4,
        "exchanges": 0,
        "max_exchanges": 3,
        "suggested_services": [],
        "parameters": {},
        "awaiting_confirmation": False
    }

def log_to_csv(user_query, refined_keywords):
    file_path = "query_logs.csv"
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["User Query", "Refined Keywords"])
    new_data = pd.DataFrame(
        {"User Query": [user_query], "Refined Keywords": [refined_keywords]}
    )
    df = pd.concat([df, new_data], ignore_index=True)
    df.to_csv(file_path, index=False)

# Ensure that the OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# Define file paths relative to the app directory
MICROSERVICES_FILE = os.path.join(os.path.dirname(__file__), "..", "langchain", "services.txt")
SUMMARY_FILE = os.path.join(os.path.dirname(__file__), "..", "langchain", "summary.txt")
PARAMS_FILE = os.path.join(os.path.dirname(__file__), "..", "langchain", "service_params.txt")

llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.7)

def prepare_system_context(microservices: List[Dict[str, str]], system_summary: str, params_list: Dict) -> str:
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
    
    # Process the response to extract services and parameters
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

def generate_summary(conversation: List[str], available_hours: int, llm: ChatOpenAI) -> str:
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
