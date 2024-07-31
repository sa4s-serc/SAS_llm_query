import re
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
from test_project_crewai.service_manager import ServiceManager
import json

LLM_MODEL = ChatOpenAI(model_name="gpt-4o-mini")
service_manager = ServiceManager()


def create_agents():
    query_agent = Agent(
        role="Query Analyzer and Router",
        goal="Analyze queries and route to appropriate services ",
        backstory=f"""You route queries to services. Available services: {service_manager.get_services()}. You never generate code
       and the code will always be geneated by refined aganet, your job is to pass a prompt to the function generator agent based on the query
      if the query is to calculate the square root of 49, the prompt would be to set up a service to calculuate square root """,
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
    )

    function_generator_agent = Agent(
        role="Service Creator",
        goal="Create new Flask services for unhandled queries",
        backstory="You create complete Flask applications for new types of queries",
        verbose=True,
        allow_delegation=False,
        llm=LLM_MODEL,
    )

    return query_agent, function_generator_agent


def create_tasks(query, query_agent, function_generator_agent):
    analyze_query_task = Task(
        description=f"""Analyze the query: '{query}'.
        Determine the type of function needed to handle this query.
        Return a JSON string with 'query_type' and 'refined_query' keys.
        Ensure your response is a valid JSON string. The refined query should be generic
        and not contain a value, for eg: calculuate square root of 49 should be refined to generate a service
        to calculuate square rooot""",
        agent=query_agent,
        expected_output="""A JSON string with:
        {
            "query_type": "descriptive name for the query type",
            "refined_query": "refined query for new service"
        }""",
    )

    generate_service_task = Task(
        description=f"""Create a new Flask service based on the refined query and query type.
        The service should run on port {{port}}.
        Return a JSON  with 'new_service_code' and 'endpoint_format' keys.
        The 'new_service_code' should be a complete Flask application that can handle the query.
        Include all necessary imports, route definitions, and the main function to run the app.
        The main route should accept POST requests with a JSON body containing a 'query' key.
        The 'endpoint_format' should describe the expected JSON format for the request.
        """,
        agent=function_generator_agent,
        expected_output="""A JSON string with:
        {
            "new_service_code": "Complete Flask application code as a string",
            "endpoint_format": "{"query": "input_value"}"
        }""",
    )

    return [analyze_query_task, generate_service_task]


def parse_raw_string(raw_string):
    # Remove triple backticks and "json" if present
    cleaned_string = re.sub(r"^```json\s*|\s*```$", "", raw_string.strip())

    try:
        # Attempt to parse the cleaned string as JSON
        json_object = json.loads(cleaned_string)
        return json_object
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return None


def process_query(query):
    query_agent, function_generator_agent = create_agents()
    tasks = create_tasks(query, query_agent, function_generator_agent)

    crew = Crew(
        agents=[query_agent, function_generator_agent],
        tasks=tasks,
        verbose=2,
    )

    result = crew.kickoff()
    result_str = parse_raw_string(result.raw)
    if result_str:
        print(json.dumps(result_str, indent=2))
    print("raw result:", result.raw)
    print("Current services: ", service_manager.get_services())
    try:
        result_dict = result_str

        if (
            isinstance(result_dict, dict)
            and "new_service_code" in result_dict
            and "endpoint_format" in result_dict
        ):
            service_code = result_dict["new_service_code"]
            endpoint_format = result_dict["endpoint_format"]
            query_type = "square_root"  # You might want to determine this dynamically

            # Get the next available port
            port = service_manager.next_port

            # Replace the hardcoded port in the service code
            service_code = service_code.replace(
                "app.run(port=5000)", f"app.run(port={port})"
            )

            new_endpoint = service_manager.create_service(service_code, query_type)
            return {
                "endpoint": new_endpoint,
                "message": "New service created",
                "endpoint_format": (
                    json.loads(endpoint_format)
                    if isinstance(endpoint_format, str)
                    else endpoint_format
                ),
            }
        else:
            return {"error": "Unexpected result format from crew"}

    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}
