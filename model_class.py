import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import subprocess

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
        code = self._generate_service(refined_query, port)
        clean_code = self._clean_generated_code(code)

        filename = f"service_{port}.py"
        with open(filename, "w") as f:
            f.write(clean_code)

        subprocess.Popen(["python", filename])

        service_info = {
            "service_endpoint": f"http://localhost:{port}/",
            "service_method": "POST",
            "request_body": {"input": "string"},
            "service_description": f"A service that {refined_query.lower()}",
        }
        self.service_manager.add_service(service_info)

        return service_info

    def _generate_service(self, refined_query, port):
        template = """
        {refined_query}

        Create a Flask application that runs on port {port}. The application should have a single POST route at '/' that receives JSON input and returns JSON output.
        Include all necessary imports.
        The service should be self-contained in a single file.
        Do not include any comments, explanations, or code block formatting in the code.
        """

        prompt = PromptTemplate(
            input_variables=["refined_query", "port"], template=template
        )

        chain = LLMChain(llm=self.llm, prompt=prompt)
        code = chain.run(refined_query=refined_query, port=port)

        return code

    def _clean_generated_code(self, code):
        code = code.replace("```python", "").replace("```", "")
        code = code.strip()
        if not code.endswith("\n"):
            code += "\n"
        return code
