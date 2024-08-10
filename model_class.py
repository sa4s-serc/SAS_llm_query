import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import subprocess
import ast

load_dotenv()
API_KEY = os.getenv("OPEN_AI_API_KEY")
MODEL = os.getenv("OPEN_AI_MODEL")


class QueryRefiner:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.llm = ChatOpenAI(model_name=MODEL, temperature=0.7)

    def refine(self, query: str):
        refined_query = self._refine_query(query)
        existing_service = self._check_existing_service(refined_query)

        if existing_service:
            print("matched existing service")
            return {
                "service_exists": True,
                "service_endpoint": existing_service["service_endpoint"],
                "service_method": existing_service["service_method"],
                "request_body": existing_service["request_body"],
                "service_description": existing_service["service_description"],
            }
        else:
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
        print(f"Services description ---> {services_descriptions} \n\n\n\n\n")
        if not services_descriptions:
            return None

        output_parser = StructuredOutputParser.from_response_schemas(
            [
                ResponseSchema(
                    name="matching_index",
                    description="The index of the matching service (0-based) or -1 if no match",
                ),
                ResponseSchema(
                    name="explanation",
                    description="Explanation for the matching decision",
                ),
            ]
        )

        format_instructions = output_parser.get_format_instructions()

        template = """
            Given the following user query and list of existing service descriptions,
            determine if any existing service can fulfill the query. If a match is found, return the index of the matching service (0-based).
            If no match is found, return -1.

            User query: {query}

            Existing service descriptions:
            {services}

            {format_instructions}
            """

        prompt = PromptTemplate(
            input_variables=["query", "services"],
            template=template,
            partial_variables={"format_instructions": format_instructions},
        )
        print(f"prompt ---> {prompt} \n\n\n\n\n")
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            query=query, services=json.dumps(services_descriptions, indent=2)
        )

        try:
            parsed_output = output_parser.parse(response)
            matching_index = int(parsed_output["matching_index"])  # Convert to int
            print(f"parsed_output ---> {parsed_output} \n\n\n\n\n")
            if matching_index >= 0 and matching_index < len(
                self.service_manager.services
            ):
                return self.service_manager.services[matching_index]
        except ValueError as e:
            print(f"Error parsing matching_index: {e}")
        except Exception as e:
            print(f"Error parsing LLM response for service matching: {e}")

        return None

    def _refine_query(self, query: str):
        template = """
            Your task is to refine the following query into a general request for writing a Python function:

            Original query: {query}

            Instructions:
            1. Analyze the query to understand the underlying task or problem.
            2. Formulate a clear and specific request for writing a Python function that addresses the general case of the query.
            3. Start your refined query with "Write a Python function to" followed by a concise description of the task.
            4. Focus on creating a reusable function that can handle various inputs, not just the specific example in the query.
            5. If the original query is vague, make reasonable assumptions and state them.
            6. Ensure the function is general enough to be used in various contexts, not just for the specific instance mentioned in the query.

            Examples:
            - If the query is "What is the square root of 49?", the refined query should be "Write a Python function to calculate the square root of any given number"
            - If the query is "Find the 5th Fibonacci number", the refined query should be "Write a Python function to calculate the nth Fibonacci number"

            Refined query: "Write a Python function to
            """

        prompt = PromptTemplate(input_variables=["query"], template=template)

        chain = LLMChain(llm=self.llm, prompt=prompt)
        refined_query = chain.run(query=query)

        return refined_query.strip()


class ServiceGenerator:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.llm = ChatOpenAI(model_name=MODEL, temperature=0.7)

    def generate(self, refined_query, port):
        service_info = self._generate_service_info(refined_query, port)

        if service_info:
            code = service_info.pop("code", None)  # Remove code from service_info
            if code:
                clean_code = self._clean_generated_code(code)
                filename = f"service_{port}.py"
                with open(filename, "w") as f:
                    f.write(clean_code)
                subprocess.Popen(["python", filename])

            self.service_manager.add_service(service_info)

        return service_info

    def _generate_service_info(self, refined_query, port):
        output_parser = StructuredOutputParser.from_response_schemas(
            [
                ResponseSchema(
                    name="code", description="The Python code for the Flask service"
                ),
                ResponseSchema(
                    name="request_body",
                    description="A dictionary describing the expected request body",
                ),
                ResponseSchema(
                    name="service_description",
                    description="A brief description of what the service does",
                ),
            ]
        )

        format_instructions = output_parser.get_format_instructions()

        template = """
        Your task is to create a Flask service based on the following refined query:
        {refined_query}

        Create a Flask application that runs on port {port}. Follow these guidelines:
        1. The application should have a single POST route at '/'.
        2. All input parameters should be received as strings in the JSON payload.
        3. Inside the route function, parse the input strings to appropriate types (int, float, etc.) as needed.
        4. Handle potential parsing errors and return appropriate error messages.
        5. The route should return the result as JSON.
        6. Include all necessary imports.
        7. The service should be self-contained in a single file.
        8. Do not include any comments or explanations in the code.
        9. Ensure proper error handling for invalid inputs.

        In addition to the code, provide:
        1. A description of the expected request body as a dictionary, where all values are "string".
        2. A brief description of what the service does.

        {format_instructions}
        """

        prompt = PromptTemplate(
            input_variables=["refined_query", "port"],
            template=template,
            partial_variables={"format_instructions": format_instructions},
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        result = chain.run(refined_query=refined_query, port=port)

        try:
            parsed_output = output_parser.parse(result)
            service_info = {
                "service_endpoint": f"http://localhost:{port}/",
                "service_method": "POST",
                "request_body": parsed_output["request_body"],
                "service_description": parsed_output["service_description"],
                "code": parsed_output[
                    "code"
                ],  # This will be removed in the generate method
            }
            return service_info
        except Exception as e:
            print(f"Error parsing LLM output: {e}")
            return None

    def _clean_generated_code(self, code):
        code = code.replace("```python", "").replace("```", "")
        code = code.strip()
        if not code.endswith("\n"):
            code += "\n"
        return code
