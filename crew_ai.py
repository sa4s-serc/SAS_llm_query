import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Ensure that the OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")

# Set up the OpenAI model
llm = ChatOpenAI(
    openai_api_key=OPENAI_API_KEY,
    model_name=OPEN_AI_MODEL,
    temperature=0.7
)

# Define the agents
alice = Agent(
    role="Friendly and outgoing individual",
    goal="To have a pleasant conversation and learn about the other person",
    backstory="Alice is a 28-year-old graphic designer who loves traveling and trying new cuisines.",
    llm=llm
)

bob = Agent(
    role="Introverted but curious individual",
    goal="To share interests and learn from the conversation",
    backstory="Bob is a 32-year-old software engineer who enjoys reading science fiction and playing chess.",
    llm=llm
)

def create_conversation_task(agent, turn_number):
    return Task(
        description=f"Continue the conversation based on the previous messages. This is turn {turn_number}.",
        agent=agent,
        expected_output="A response that continues the conversation naturally, asking questions or sharing relevant information."
    )

# Create tasks for the conversation
max_turns = 5  # Set the number of turns for each agent
tasks = []
for turn in range(max_turns * 2):  # Total turns will be max_turns * 2
    current_agent = alice if turn % 2 == 0 else bob
    task = create_conversation_task(current_agent, turn + 1)
    tasks.append(task)

# Create the crew with all tasks
conversation_crew = Crew(
    agents=[alice, bob],
    tasks=tasks,
    verbose=True
)

# Run the conversation
result = conversation_crew.kickoff()

print("\nFull conversation:")
for task in tasks:
    print(f"\nTurn {task.description.split()[-1]} - {task.agent.role}:")
    print(task.output.raw if task.output else "No output")

print("\nFinal result:")
print(result)