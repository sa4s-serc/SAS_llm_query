from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import json
from fuzzywuzzy import fuzz

# Initialize the LLM model
LLM_MODEL = ChatOpenAI(model_name="gpt-4o-mini")

# Cache to store generated functions
function_cache = {}

# Define the Query Agent
query_agent = Agent(
    role="Query Analyzer and Router",
    goal="Accurately analyze incoming queries and route them to appropriate endpoints or the Function Generator Agent",
    backstory="""You are an expert in query analysis and routing with extensive knowledge of the current system's capabilities.
    The existing endpoints are:
    1. /sqrt/<float:number> (GET): Calculates the square root of a given number.
    2. /prime/<int:number> (GET): Checks if a given number is prime.
    3. /factorial/<int:number> (GET): Calculates the factorial of a given number.
    4. /query (POST): Handles general queries that don't fit the above endpoints.

    Your job is to understand the user's query, check if existing endpoints can handle it, and if not, refine the query for the Function Generator Agent.
    You must NEVER write code yourself. You must ALWAYS consider the existing endpoints first before suggesting a new function.""",
    verbose=True,
    allow_delegation=False,
    llm=LLM_MODEL,
)

# Define the Function Generator Agent
function_generator_agent = Agent(
    role="Function Implementer",
    goal="Generate Python code based on refined queries",
    backstory="""You are a skilled Python programmer. Your task is to implement Python functions based on refined queries that cannot be handled by existing endpoints.
    You must ONLY provide the Python function code, without any explanations, usage examples, or test cases.""",
    verbose=True,
    allow_delegation=False,
    llm=LLM_MODEL,
)

analyze_query_task = Task(
    description="Analyze the incoming query: '{query}'. Follow these steps:\n"
    "1. Understand the query's intent and required computation.\n"
    "2. Check if any existing endpoints (sqrt, prime, factorial) can handle the query.\n"
    "3. If an existing endpoint can handle it, return a JSON object with the 'endpoint' key and the endpoint as the value.\n"
    "4. If no existing endpoint is suitable, return a JSON object with the 'refined_query' key and the refined query as the value.\n"
    "5. NEVER write code in your response.\n"
    "6. ALWAYS consider the limitations and capabilities of the existing endpoints before suggesting a new function.",
    agent=query_agent,
    expected_output="A JSON object with either an 'endpoint' or a 'refined_query' key",
)

generate_function_task = Task(
    description="Based on the refined query: '{query}', implement a Python function.\n"
    "Provide ONLY the Python function code, without any explanations, usage examples, or test cases.",
    agent=function_generator_agent,
    expected_output="A Python function implementation without any additional text",
)

route_query_task = Task(
    description="Based on the analysis of the query: '{query}' or new function:\n"
    "1. If an existing endpoint can handle the query, return the JSON object with the 'endpoint' key.\n"
    "2. If a new function was implemented, return the JSON object with the 'function_code' key and the function code as the value.\n"
    "3. NEVER generate code yourself. Only use the function provided by the Function Generator Agent.",
    agent=query_agent,
    expected_output="A JSON object with either an 'endpoint' or a 'function_code' key",
)
# Create the crew
query_processing_crew = Crew(
    agents=[query_agent, function_generator_agent],
    tasks=[analyze_query_task, generate_function_task, route_query_task],
    verbose=2,  # You can adjust this for different levels of output
)


def find_similar_query(query, threshold=80):
    for cached_query in function_cache:
        similarity = fuzz.ratio(query.lower(), cached_query.lower())
        if similarity >= threshold:
            return cached_query
    return None


def process_query(query):
    # Check if a similar query exists in the cache
    similar_query = find_similar_query(query)
    if similar_query:
        return {"function_code": function_cache[similar_query]}

    crew_output = query_processing_crew.kickoff(inputs={"query": query})

    try:
        result = json.loads(crew_output.raw)
        print(result)
        if "endpoint" in result:
            return {"endpoint": result["endpoint"]}
        elif "function_code" in result:
            function_cache[query] = result["function_code"]
            return {"function_code": result["function_code"]}
    except json.JSONDecodeError:
        pass

    return {"error": "Unable to process query"}
