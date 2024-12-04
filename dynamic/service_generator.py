import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import subprocess

load_dotenv()
API_KEY = os.getenv("OPEN_AI_API_KEY")
MODEL = os.getenv("OPEN_AI_MODEL")

class ServiceGenerator:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.llm = ChatOpenAI(model_name=MODEL, temperature=0.7)

    def generate(
        self,
        refined_query,
        port,
        needs_json_data,
        json_data_info=None,
        http_method="POST",
    ):
        service_info = self._generate_service_info(
            refined_query, port, needs_json_data, json_data_info, http_method
        )

        if service_info:
            code = service_info.pop("code", None)
            if code:
                clean_code = self._clean_generated_code(code)
                filename = f"services/service_{port}.py"
                with open(filename, "w") as f:
                    f.write(clean_code)
                subprocess.Popen(["python", filename])

            self.service_manager.add_service(service_info)

        return service_info

    def _generate_service_info(
        self,
        refined_query,
        port,
        needs_json_data,
        json_data_info=None,
        http_method="POST",
    ):
        output_parser = StructuredOutputParser.from_response_schemas(
            [
                ResponseSchema(
                    name="code", 
                    description="The complete Python code for the FastAPI microservice"
                ),
                ResponseSchema(
                    name="request_body",
                    description="A description of the Pydantic model for request parameters",
                ),
                ResponseSchema(
                    name="service_description",
                    description="A brief description of what the service does",
                ),
            ]
        )

        format_instructions = output_parser.get_format_instructions()

        system_template = """You are an AI assistant specializing in creating FastAPI microservices following a specific pattern.
        Your task is to generate a complete FastAPI service that follows these exact structural requirements:

        1. Class Structure:
           - Main service class must inherit from MicroserviceBase
           - Use descriptive service name in super().__init__("service_name")
           - Must include update_service_info with clear description and empty dependencies list
           - Must have proper data loading method with error handling
           - Must follow the register_routes and process_request pattern

        2. Pydantic Models:
           - Create Params model for request parameters (e.g., ExhibitionTrackerParams)
           - Always use Optional[List[str]] for string parameters that can be multiple
           - Always use Optional[str] for timestamp parameters
           - Use Optional[List[int]] for numeric list parameters
           - Include proper field descriptions and validations

        3. Data Processing:
           - Convert single string inputs to lists when needed
           - Include proper timestamp handling where required
           - Group data by relevant fields when needed
           - Apply filters in a consistent order
           - Log the count of items after each filter

        4. Response Format:
           - For list responses: {{"items": [...], "message": "Found X items matching criteria"}}
           - For single item responses: Return the item with relevant fields
           - Empty results: {{"items": [], "message": "No items found matching criteria"}}
           - Always include proper error messages

        5. Error Handling and Logging:
           - Log at start of request processing
           - Log after each filter operation
           - Log final result count
           - Include try-except in data loading
           - Handle all parameter type conversions safely

        You must use the provided JSON data source information:
        {json_data_info}
        """

        human_template = """
        Create a FastAPI microservice based on the following refined query:
        {refined_query}

        The service should run on port {port} and use the {http_method} method.

        Follow these exact implementation patterns:

        1. Service Class Structure:
        ```python
        class ServiceNameService(MicroserviceBase):
            def __init__(self):
                super().__init__("service_name")
                self.update_service_info(
                    description="Service specific description",
                    dependencies=[]
                )
                self.data = self.load_data()

            def load_data(self):
                try:
                    with open('{data_path}', 'r') as f:
                        return json.load(f)
                except FileNotFoundError:
                    self.logger.error("{data_path} not found")
                    return []
                except json.JSONDecodeError:
                    self.logger.error("Error decoding {data_path}")
                    return []
        ```

        2. Route Registration:
        ```python
        def register_routes(self):
            @self.app.post("/endpoint")
            async def endpoint(params: ParamsModel):
                self.logger.info("Processing request with params: " + str(params))
                return await self.process_request(params.dict(exclude_unset=True))
        ```

        3. Request Processing:
        ```python
        async def process_request(self, params):
            self.logger.info("Processing request with params: " + str(params))
            filtered_data = self.data

            # Handle list parameters
            if params.get('list_param'):
                values = params['list_param']
                if isinstance(values, str):
                    values = [values]
                filtered_data = [d for d in filtered_data if d['field'] in values]
                self.logger.info("After filter: " + str(len(filtered_data)) + " items")

            if not filtered_data:
                return {{"items": [], "message": "No items found matching criteria"}}
            
            return {{"items": filtered_data, "message": "Found " + str(len(filtered_data)) + " matching items"}}
        ```

        {json_instructions}

        {format_instructions}
        Make sure to include correct imports, proper data path usage, and the service running code.
        """

        if needs_json_data and json_data_info:
            json_data_info_str = json.dumps(json_data_info, indent=2)
            json_info = (
                f"You have access to the following JSON data sources:\n{json_data_info_str}"
            )
            data_path = json_data_info[0]["path"] if json_data_info else "data/specific_data.json"
            json_instructions = """The service must:
            1. Use the exact JSON file path from the data source info
            2. Follow the JSON schema for data processing
            3. Handle all fields defined in the schema
            4. Include proper validation for all data fields
            5. Handle data loading errors gracefully"""
        else:
            print("Does not require json access ")
            json_info = "This query does not require JSON data access."
            json_instructions = ""
            data_path = "data/specific_data.json"

        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        ).format(json_data_info=json_info)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        result = chain.run(
            refined_query=refined_query,
            port=port,
            http_method=http_method,
            json_instructions=json_instructions,
            format_instructions=format_instructions,
            data_path=data_path
        )

        try:
            parsed_output = output_parser.parse(result)
            service_info = {
                "service_endpoint": f"http://localhost:{port}/",
                "service_method": http_method,
                "request_body": parsed_output["request_body"],
                "service_description": parsed_output["service_description"],
                "code": parsed_output["code"],
                "data_path": data_path
            }
            return service_info
        except Exception as e:
            print(f"Error in service generation: {e}")
            return None

    def _clean_generated_code(self, code):
        code = code.replace("```python", "").replace("```", "")
        code = code.replace("\\n", "\n")
        code = code.strip()
        if not code.endswith("\n"):
            code += "\n"
        return code