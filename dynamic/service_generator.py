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

load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL")

class ServiceGenerator:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.llm = ChatOpenAI(model_name=MODEL, temperature=0.7)
        self.output_dir = "app/generated_services"
        
        # Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
    def generate(
        self,
        refined_query,
        needs_json_data,
        json_data_info=None,
        http_method="POST",
        service_name=None
    ):
        service_info = self._generate_service_info(
            refined_query, needs_json_data, json_data_info, http_method, service_name
        )

        if service_info:
            code = service_info.pop("code", None)
            if code:
                clean_code = self._clean_generated_code(code)
                service_name = service_info["service_name"]
                
                # Create service directory if it doesn't exist
                service_dir = os.path.join(self.output_dir, service_name)
                if not os.path.exists(service_dir):
                    os.makedirs(service_dir)
                
                # Save service file
                service_file = os.path.join(service_dir, "service.py")
                with open(service_file, "w") as f:
                    f.write(clean_code)
                
                # Create __init__.py
                init_file = os.path.join(service_dir, "__init__.py")
                if not os.path.exists(init_file):
                    with open(init_file, "w") as f:
                        f.write("")

            self.service_manager.add_service(service_info)

        return service_info

    def _generate_service_info(
        self,
        refined_query,
        needs_json_data,
        json_data_info=None,
        http_method="POST",
        service_name=None
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
                ResponseSchema(
                    name="service_name",
                    description="The name of the service in snake_case format without _service suffix",
                ),
            ]
        )

        format_instructions = output_parser.get_format_instructions()

        system_template = """You are an AI assistant specializing in creating FastAPI microservices following a specific pattern.
        Your task is to generate a complete FastAPI service that follows these exact requirements:

        1. Must include these exact imports at the top:
        ```python
        import json
        from fastapi import HTTPException
        from pydantic import BaseModel
        from typing import Optional, List
        from app.microservices.base import MicroserviceBase
        from datetime import datetime
        ```

        2. Must follow this exact class pattern:
        ```python
        class ServiceNameParams(BaseModel):
            # Parameters with exact types
            param1: Optional[List[str]] = None
            param2: Optional[str] = None

        class ServiceNameService(MicroserviceBase):
            def __init__(self):
                super().__init__("service_name")
                self.update_service_info(
                    description="Service description",
                    dependencies=[]
                )
                self.data = self.load_data()

            def load_data(self):
                try:
                    with open('data/file.json', 'r') as f:
                        return json.load(f)
                except FileNotFoundError:
                    self.logger.error("file.json not found")
                    return []
                except json.JSONDecodeError:
                    self.logger.error("Error decoding file.json")
                    return []

            def register_routes(self):
                @self.app.post("/endpoint")
                async def endpoint_handler(params: ServiceNameParams):
                    self.logger.info(f"Received parameters: {{params}}")
                    return await self.process_request(params.dict(exclude_unset=True))

            async def process_request(self, params):
                self.logger.info(f"Processing request with params: {{params}}")
                # Process logic here
                return {{"results": [], "message": "Message"}}

        def start_service_name():
            service = ServiceNameService()
            service.run()

        if __name__ == "__main__":
            start_service_name()
        ```

        3. Must follow these exact patterns:
        - Use Optional[List[str]] for string list parameters
        - Use Optional[str] for single string parameters
        - Use Optional[int] for integer parameters
        - Always use self.logger for logging
        - Always return dict with results and message
        - Always handle type conversions in process_request
        - Always use params.dict(exclude_unset=True) in route handler
        - Never pass app to run() method
        - Always use async/await for route handlers and process_request

        The data source information provided must be used exactly as specified:
        {json_data_info}
        """

        human_template = """
        Create a FastAPI microservice based on the following refined query:
        {refined_query}

        Use this EXACT data path: {data_path}
        
        Follow this EXACT schema for the Pydantic model:
        {schema}

        The service MUST:
        1. Use exact service name: {service_name}
        2. Use exact endpoint: /{service_name}
        3. Match parameter names and types exactly
        4. Follow error handling pattern exactly
        5. Use proper logging with self.logger
        6. Return results in the exact format as shown
        7. Handle type conversions properly
        8. Use async/await correctly
        9. Not pass app to run() method

        {json_instructions}

        {format_instructions}
        """

        if needs_json_data and json_data_info:
            data_source = json_data_info[0]  # Use first data source
            data_path = data_source["path"]
            schema = json.dumps(data_source["schema"], indent=2)
            json_instructions = """The service must:
            1. Use the exact JSON file path provided
            2. Follow the JSON schema exactly
            3. Handle all fields defined in the schema
            4. Include proper validation
            5. Handle data loading errors appropriately for the data structure"""
        else:
            data_path = "data/specific_data.json"
            schema = "{}"
            json_instructions = ""

        # Convert service name to class name format
        service_class_name = "".join(word.capitalize() for word in (service_name or "").split("_")) + "Service"

        # Format the templates with all required variables
        system_message = SystemMessagePromptTemplate.from_template(system_template)
        human_message = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages([
            system_message,
            human_message
        ])

        # Create a dictionary with all required template variables
        template_vars = {
            "refined_query": refined_query,
            "json_instructions": json_instructions,
            "format_instructions": format_instructions,
            "data_path": data_path,
            "schema": schema,
            "service_name": service_name or "",
            "service_class_name": service_class_name,
            "json_data_info": json.dumps(json_data_info, indent=2) if json_data_info else "None"
        }

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        result = chain.run(**template_vars)

        try:
            parsed_output = output_parser.parse(result)
            # Use provided service name or parsed one
            final_service_name = service_name or parsed_output["service_name"].replace("_service", "")
            service_info = {
                "service_name": final_service_name,
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