import os
from openai import OpenAI
from flask import Flask
import json
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPEN_AI_API_KEY")
MODEL = os.getenv("OPEN_AI_MODEL")
# Initialize the OpenAI client
client = OpenAI(api_key=API_KEY)


class QueryRefiner:
    def __init__(self, service_manager):
        self.service_manager = service_manager

    def refine(self, query: str):
        # Use LLM to check if a service exists for this query
        existing_service = self._check_existing_service(query)

        if existing_service:
            print("matched existing service")
            return {
                "service_exists": True,
                "service_endpoint": existing_service["service_endpoint"],
                "service_method": existing_service["service_method"],
                "request_body": existing_service["request_body"],
            }
        else:
            # Use OpenAI to refine the query
            refined_query = self._refine_query(query)
            print(f"Refined query --> {refined_query}")
            suggested_port = self.service_manager.get_next_available_port()
            return {
                "service_exists": False,
                "refined_query": refined_query,
                "suggested_port": suggested_port,
                "service_description": f"A service that {refined_query.lower()}",
            }

    def _check_existing_service(self, query: str):
        services_descriptions = self.service_manager.get_services_descriptions()

        if not services_descriptions:
            return None

        prompt = f"""
        Given the following user query and list of existing service descriptions,
        determine if any existing service can fulfill the query. If a match is found, return the index of the matching service (0-based).
        If no match is found, return -1.

        User query: "{query}"

        Existing service descriptions:
        {json.dumps(services_descriptions, indent=2)}

        Response format: {{
            "matching_index": int,
            "explanation": str
        }}

        Provide your response in valid JSON format.
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an AI assistant tasked with matching user queries to existing services based on their descriptions.
                    Analyze the query and service descriptions carefully to find the best match, if any exists.
                    """,
                },
                {"role": "user", "content": prompt},
            ],
        )

        try:
            result = json.loads(response.choices[0].message.content.strip())
            matching_index = result["matching_index"]

            if matching_index >= 0 and matching_index < len(
                self.service_manager.services
            ):
                return self.service_manager.services[matching_index]
        except (json.JSONDecodeError, KeyError, IndexError):
            print("Error parsing LLM response for service matching.")

        return None

    def _refine_query(self, query: str):
        prompt = f"""
        Your task is to refine the following query into a specific request for writing Python code:

        Original query: "{query}"

        Instructions:
        1. Analyze the query to understand the underlying task or problem.
        2. Formulate a clear and specific request for writing Python code that addresses the query.
        3. Start your refined query with "Write Python code to" followed by a concise description of the task.
        4. Focus on the core functionality required, avoiding unnecessary details.
        5. If the original query is vague, make reasonable assumptions and state them.

        Refined query: "Write Python code to
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": """
                    You are an expert system designed to refine user queries into specific requests for writing Python code. Your role is to:

                    1. Interpret the user's intent accurately, even if the query is vague or ambiguous.
                    2. Formulate clear, concise, and specific requests for Python code that address the core of the user's query.
                    3. Focus on the essential functionality required, without adding unnecessary complexity.
                    4. If the query involves multiple steps or components, break it down into a single, primary coding task.
                    5. Avoid writing actual code; instead, provide a prompt that guides a developer to write the appropriate code.
                    6. Ensure your refined query starts with "Write Python code to" followed by a clear, actionable description.

                    Examples:
                    - Input: "What's the weather like?"
                      Output: "Write Python code to fetch current weather data for a given location using an API"
                    - Input: "Help me organize my tasks"
                      Output: "Write Python code to create a simple command-line to-do list manager with add, remove, and list functions"
                    - Input: "Calculate compound interest"
                      Output: "Write Python code to calculate compound interest given principal, rate, time, and compounding frequency"
                    """,
                },
                {"role": "user", "content": prompt},
            ],
        )

        refined_query = response.choices[0].message.content.strip()
        return refined_query


class ServiceGenerator:
    def __init__(self, service_manager):
        self.service_manager = service_manager

    def generate(self, refined_query, port):
        # Use OpenAI to generate code based on the refined query
        code = self._generate_service(refined_query, port)

        # Clean up the generated code
        clean_code = self._clean_generated_code(code)

        # Save the code to a file
        filename = f"service_{port}.py"
        with open(filename, "w") as f:
            f.write(clean_code)

        # Start the service (in a real scenario, you'd want to do this more robustly)
        import subprocess

        subprocess.Popen(["python", filename])

        # Register the service with the service manager
        service_info = {
            "service_endpoint": f"http://localhost:{port}/",
            "service_method": "POST",
            "request_body": {"input": "string"},
            "service_description": f"A service that {refined_query.lower()}",
        }
        self.service_manager.add_service(service_info)

        return service_info

    def _generate_service(self, refined_query, port):
        prompt = f"""
        {refined_query}

        Create a Flask application that runs on port {port}. The application should have a single POST route at '/' that receives JSON input and returns JSON output.
        Include all necessary imports.
        The service should be self-contained in a single file.
        Do not include any comments, explanations, or code block formatting in the code.
        """

        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that generates Python code for Flask applications.",
                },
                {"role": "user", "content": prompt},
            ],
        )

        code = response.choices[0].message.content.strip()
        return code

    def _clean_generated_code(self, code):
        # Remove any remaining code block indicators
        code = code.replace("```python", "").replace("```", "")

        # Remove any leading or trailing whitespace
        code = code.strip()

        # Ensure there's a newline at the end of the file
        if not code.endswith("\n"):
            code += "\n"

        return code
