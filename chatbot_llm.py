import os
from typing import List, Dict, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv
from utils import load_microservices, get_user_goal, load_summary, load_service_parameters

# Load environment variables from a .env file if present
load_dotenv()

# Ensure that the OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
if not OPEN_AI_MODEL:
    raise ValueError("Please set the OPEN_AI_MODEL environment variable.")

# Define file paths
MICROSERVICES_FILE = "services.txt"
SUMMARY_FILE = "summary.txt"
PARAMS_FILE = "service_params.txt"

def prepare_system_context(microservices: List[Dict[str, str]], system_summary: str, params_list: Dict) -> str:
    """
    Prepares the system context including service parameters.
    """
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
    """
    Identifies relevant services and their parameters based on the conversation.
    """
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
    """
    Generates a summary of the tourist's focused plan based on the conversation.
    """
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

def main():
    # Load all required data
    microservices = load_microservices(MICROSERVICES_FILE)
    system_summary = load_summary(SUMMARY_FILE)
    params_list = load_service_parameters(PARAMS_FILE)
    
    if not microservices:
        print("No services found. Please check the services.txt file.")
        return

    # Initialize the ChatOpenAI LLM
    llm = ChatOpenAI(api_key=OPENAI_API_KEY, temperature=0.7, model=OPEN_AI_MODEL)


    available_hours = 4  # You can modify this or make it dynamic

    conversation_history = []
    
    system_prompt = prepare_system_context(microservices, system_summary, params_list)
    conversation_history.append(SystemMessage(content=system_prompt))

    print("\n"*5)
    prompt_count = 0
    max_turns = 3
    
    while prompt_count < max_turns:
# For the first message
        if prompt_count == 0:
            assistant_messages = conversation_history + [HumanMessage(content="""
                Start with a warm greeting and introduce yourself as a Hyderabad guide.
                Ask the visitor about their interests and how much time they have to explore.
                Keep it natural and friendly.
            """)]
        else:
            # For subsequent messages
            assistant_messages = conversation_history + [HumanMessage(content=f"""
                As a Hyderabad City Guide, respond naturally to the tourist.
                Build on the previous conversation.
                Ask relevant follow-up questions based on their responses.
                Suggest activities only if enough context is available.
                Keep the conversation natural and informative.
            """)]
        
        assistant_response = llm(assistant_messages)
        print(f"Assistant: {assistant_response.content}")

        # Append assistant's response to the conversation history
        conversation_history.append(assistant_response)

        # Get user input
        user_input = input("You: ").strip()
        if user_input.lower() in {"exit", "quit", "bye", "goodbye"}:
            print("Thank you for chatting! I hope you enjoy your time in Hyderabad!")
            break

        if not user_input:
            print("I didn't catch that. Could you please repeat?")
            continue

        # Append user input to the conversation history
        conversation_history.append(HumanMessage(content=user_input))

        prompt_count += 1

        # Identify and print relevant services and parameters after each turn
        identified_services, service_params = identify_services_and_params(
            [msg.content for msg in conversation_history],
            microservices,
            params_list,
            llm
        )
        
        print("\n(not llm) Identified services and parameters so far:")
        for service in identified_services:
            if len(service_params[service].items()) == 0: continue
            print(f"- {service}:")
            for param, values in service_params[service].items():
                print(f"  {param}: {', '.join(values)}")

        # After max turns or if user exits, generate summary
        if prompt_count == max_turns:
            summary = generate_summary([msg.content for msg in conversation_history], available_hours, llm)
            print(f"\nAssistant: {summary}\nIs this what you were looking for?")

            user_confirmation = input("You (yes/no): ").strip().lower()
            if user_confirmation in ['yes', 'y']:
                print("Great! I understand what you're looking for.")
                break
            else:
                print("Let me better understand your interests.")
                prompt_count = 0  # Reset the count to continue the conversation
                continue

    # Final identification of relevant services and parameters
    final_services, final_params = identify_services_and_params(
        [msg.content for msg in conversation_history],
        microservices,
        params_list,
        llm
    )

    print("\nBased on our conversation, here are the relevant services and options:")
    for service in final_services:
        print(f"\n{service}:")
        for param, values in final_params[service].items():
            print(f"- {param}: {', '.join(values)}")

if __name__ == "__main__":
    main()