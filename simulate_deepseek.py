import sys
import os
import random
from typing import List, Dict
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from langchain_openai import ChatOpenAI
from utils import load_microservices, get_user_goal, load_summary, load_service_parameters

# Load environment variables
load_dotenv()
max_turns = 3

# Ensure OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")

if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")
if not OPEN_AI_MODEL:
    raise ValueError("Please set the OPEN_AI_MODEL environment variable.")

# Set up the OpenAI model
# llm = LLM(
#     model="deepseek/deepseek-chat",
#     temperature=0.7
# )

llm = ChatOpenAI(
    model='deepseek/deepseek-chat', 
    openai_api_key=OPENAI_API_KEY, 
    openai_api_base='https://api.deepseek.com',
)

print("Using model: ", llm.model_name) 
# Load all required files
MICROSERVICES_FILE = "services.txt"
SUMMARY_FILE = "summary.txt"
PARAMS_FILE = "service_params.txt"

microservices = load_microservices(MICROSERVICES_FILE)
system_summary = load_summary(SUMMARY_FILE)
params_list = load_service_parameters(PARAMS_FILE)

# Format parameters for agent context
params_context = "\n".join([
    f"Service '{service}' options: " + 
    ", ".join([f"{param}: {', '.join(values)}" for param, values in params.items()])
    for service, params in params_list.items()
])

# Define the agents
user_goal = get_user_goal()
available_hours = random.randint(2, 5)

tourist_agent = Agent(
    role="Hyderabad Tourist",
    goal=f"To explore Hyderabad and {user_goal} within {available_hours} hours",
    backstory=f"""You are a tourist visiting Hyderabad with {available_hours} hours to spare. 
    Your main interest is: {user_goal}. 
    You want to learn about the area and make the most of your time.
    You communicate naturally and ask relevant follow-up questions.""",
    llm=llm
)

assistant_agent = Agent(
    role="Hyderabad City Guide",
    goal="To assist tourists efficiently while maintaining consistency in recommendations",
    backstory=f"""You are a knowledgeable guide for Hyderabad, helping tourists plan their visit. 
    {system_summary}
    
    Available service options:
    {params_context}
    
    Important guidelines:
    1. Suggest only 2-3 locations/activities per response
    2. Stay consistent with your recommendations throughout
    3. Keep the original goal in mind when making suggestions
    4. Consider time constraints when planning""",
    llm=llm
)

def create_conversation_task(agent, turn_number, is_tourist=False, identified_services=None):
    if is_tourist:
        if turn_number == 1:
            description = f"""Start the conversation naturally:
            - Express your main interest: {user_goal}
            - Ask about specific types of local experiences
            - Mention your {available_hours} hour time constraint"""
        elif turn_number == 3:
            description = f"""Based on the guide's suggestions:
            - Show interest in one or two mentioned places
            - Ask specific questions about those places
            - Express any particular preferences"""
        else:
            description = f"""For your final response:
            - Confirm interest in the suggested itinerary
            - Ask any final questions about timing or logistics
            - Show enthusiasm about the planned activities"""
    else:
        services_context = f"Previously identified services: {', '.join(identified_services) if identified_services else 'None'}"
        if turn_number == 2:
            description = f"""{services_context}
            Provide a focused initial response:
            - Suggest 2-3 specific places that match their interests
            - Stay true to their desire for {user_goal}
            - Ask about specific preferences
            Keep suggestions limited and focused."""
        elif turn_number == 4:
            description = f"""{services_context}
            Build upon your previous suggestions:
            - Add details about previously mentioned places
            - Suggest 1-2 complementary activities nearby
            - Maintain consistency with earlier recommendations"""
        else:
            description = f"""{services_context}
            Provide a final focused response:
            - Give specific timing for mentioned activities
            - Stick to previously suggested locations
            - Add any essential final details"""
    
    return Task(
        description=description,
        agent=agent,
        expected_output="A natural conversational response with consistent recommendations."
    )

def create_service_identification_task(agent, conversation_history, turn_number):
    history_text = "\n".join([f"{role}: {text}" for role, text in conversation_history])
    return Task(
        description=f"""Based on the conversation so far, identify relevant services:
        Available services: {', '.join([ms['name'] for ms in microservices])}
        
        Original goal: {user_goal}
        Conversation history:
        {history_text}
        
        Return only the most relevant services as a comma-separated list.""",
        agent=agent,
        expected_output="Comma-separated list of relevant services"
    )

# Create tasks for the conversation
tasks = []
conversation_history = []
identified_services = set()

# Create main conversation tasks with service tracking
for turn in range(max_turns * 2):
    current_agent = tourist_agent if turn % 2 == 0 else assistant_agent
    is_tourist = turn % 2 == 0
    
    # Create conversation task
    conv_task = create_conversation_task(
        current_agent, 
        turn + 1, 
        is_tourist, 
        identified_services if not is_tourist else None
    )
    tasks.append(conv_task)
    
    # After guide responses, identify services
    if not is_tourist:
        track_task = create_service_identification_task(
            assistant_agent,
            conversation_history.copy(),
            turn + 1
        )
        tasks.append(track_task)
    
    conversation_history.append(
        ("Tourist" if is_tourist else "Guide", f"{{output}}")
    )

# Final summary task
tasks.append(Task(
    description=f"""Create a focused summary of the tourist's plan based ONLY on what was discussed:
    - Reference only places and activities mentioned in our conversation
    - Maintain consistency with timing preferences
    - Keep within {available_hours} hours
    
    Guidelines:
    - Don't introduce new locations not previously discussed
    - Keep focus on the original goal: {user_goal}
    - Include specific timing for activities
    
    Start with 'Based on our discussion, your plan includes...'""",
    agent=assistant_agent,
    expected_output="A concise summary of actually discussed activities."
))

# Final service parameters task
tasks.append(Task(
    description=f"""Based on the final conversation and original goal: {user_goal}
    List only the most relevant services and parameters.

    Format your response EXACTLY like this example:
    
    restaurant_finder:
    - cuisine_type: [south indian, hyderabadi]
    - dietary_restrictions: [vegetarian]

    crowd_monitor:
    - location_name: [charminar, laad bazaar]

    Guidelines:
    - Include ONLY services discussed in conversation
    - Maintain exact format with dashes and square brackets
    - List parameters under each service with correct indentation
    - Use only values from:
    {params_context}""",
    agent=assistant_agent,
    expected_output="A structured list of services and parameters in the specified format."
))

# Create crew
conversation_crew = Crew(
    agents=[tourist_agent, assistant_agent],
    tasks=tasks,
    verbose=True
)

# Run the conversation

conversation_crew.calculate_usage_metrics()
# Print results
def main(output_file):
    result = conversation_crew.kickoff()
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write usage metrics
        f.write("Usage Metrics:\n")
        f.write(str(conversation_crew.usage_metrics) + "\n")
        conversation_crew.calculate_usage_metrics()
        
        # Write conversation with service tracking
        f.write("\nConversation with Service Tracking:\n")
        service_index = 0
        for i, task in enumerate(tasks[:-2]):
            if task.agent.role == "Hyderabad Tourist":
                f.write("\nTourist:\n")
                f.write(task.output.raw if task.output else "No output")
                f.write("\n")
            elif task.agent.role == "Hyderabad City Guide":
                f.write("\nGuide:\n")
                f.write(task.output.raw if task.output else "No output")
                f.write("\n")
                service_index += 1
                next_task = tasks[i + 1]
                f.write(f"\nIdentified Services after Turn {service_index}:\n")
                f.write(next_task.output.raw if next_task.output else "No services identified")
                f.write("\n")

        # Write final summary and services
        f.write("\nFinal Plan Summary:\n")
        f.write(tasks[-2].output.raw if tasks[-2].output else "No summary provided")
        f.write("\n")

        f.write("\nOriginal Goal: ")
        f.write(str(user_goal))
        f.write("\n")

        f.write("\nCore Services and Parameters:\n")
        f.write(tasks[-1].output.raw if tasks[-1].output else "No services identified")
        f.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simulate.py <output_filename>")
        sys.exit(1)
    
    output_file = sys.argv[1]
    main(output_file)
