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
    role="Function Specification Designer and Implementer",
    goal="Generate detailed and implementable function specifications and Python code based on refined queries",
    backstory="""You are a skilled function designer and Python programmer with a deep understanding of software architecture and API design.
    Your task is to create detailed function specifications and implement them in Python based on refined queries that cannot be handled by existing endpoints.
    You provide:
    1. Function name
    2. Input parameters (types and descriptions)
    3. Expected output (type and description)
    4. Brief description of the function's purpose
    5. Any potential edge cases or error handling considerations
    6. Python implementation of the function

    Your specifications and implementations should be detailed enough for immediate use without additional clarification.""",
    verbose=True,
    allow_delegation=False,
    llm=LLM_MODEL,
)

analyze_query_task = Task(
    description="""Analyze the incoming query: '{query}'. Follow these steps:
    1. Understand the query's intent and required computation.
    2. Check if any existing endpoints (sqrt, prime, factorial) can handle the query.
    3. If an existing endpoint can handle it, specify which one and how to use it.
    4. If no existing endpoint is suitable, refine the query for the Function Generator Agent.
    5. NEVER write code in your response.
    6. ALWAYS consider the limitations and capabilities of the existing endpoints before suggesting a new function.""",
    agent=query_agent,
    expected_output="""A detailed analysis including:
    1. Query intent
    2. Whether an existing endpoint can handle it (specify which one if applicable)
    3. If not, a refined query for the Function Generator Agent
    4. Reasoning behind the decision""",
)

generate_function_task = Task(
    description="""Based on the refined query: '{query}', generate a detailed function specification and Python implementation. Include:
    1. Function name
    2. Input parameters (types and descriptions)
    3. Expected output (type and description)
    4. Brief description of the function's purpose
    5. Any potential edge cases or error handling considerations
    6. Python implementation of the function""",
    agent=function_generator_agent,
    expected_output="""A detailed function specification and Python implementation including all requested elements:
    1. Function name
    2. Input parameters
    3. Expected output
    4. Function purpose
    5. Edge cases and error handling considerations
    6. Python code for the function""",
)

route_query_task = Task(
    description="""Based on the analysis of the query: '{query}' or new function specification:
    1. If an existing endpoint can handle the query, provide the exact endpoint and how to use it.
    2. If a new function was specified, summarize the specification, provide the Python implementation, and indicate that it has been added to the cache.
    3. NEVER generate code yourself. Only use the function provided by the Function Generator Agent.
    4. Provide a clear, user-friendly response explaining how the query will be handled.""",
    agent=query_agent,
    expected_output="""A comprehensive response including:
    1. The appropriate endpoint or new function specification and implementation
    2. Clear instructions on how to use the endpoint or function
    3. A user-friendly explanation of how the query is being handled""",
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
        return {"result": "Cached result", "function": function_cache[similar_query]}

    crew_output = query_processing_crew.kickoff(inputs={"query": query})

    result = {
        "raw": str(crew_output.raw),
        "token_usage": crew_output.token_usage,
    }

    if hasattr(crew_output, "json_dict") and crew_output.json_dict:
        result["json_output"] = crew_output.json_dict

    if hasattr(crew_output, "pydantic"):
        result["pydantic_output"] = str(crew_output.pydantic)

    # Extract function code if present
    function_code = None
    if "```python" in result["raw"]:
        function_code = result["raw"].split("```python")[1].split("```")[0].strip()
        result["function_code"] = function_code

    # Cache the result if a new function was generated
    if function_code:
        function_cache[query] = function_code

    return result
