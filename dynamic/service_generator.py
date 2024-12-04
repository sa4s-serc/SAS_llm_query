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
        Your task is to generate a complete FastAPI service that follows these exact requirements:

        1. Must include these exact imports:
        import json
        from fastapi import HTTPException
        from pydantic import BaseModel
        from typing import Optional, List
        from app.microservices.base import MicroserviceBase

        2. Must use these exact patterns:
        - Main service class inherits from MicroserviceBase
        - Pydantic models use Optional[List[str]] for string lists
        - Pydantic models use Optional[str] for single strings
        - Pydantic models use Optional[List[int]] for integer lists
        - Use exact data paths from json_data_info
        - Must end with start_service function and main block

        The data source information provided must be used exactly as specified:
        {json_data_info}
        """

        human_template = """
        Create a FastAPI microservice based on the following refined query:
        {refined_query}

        The service should run on port {port} and use the {http_method} method.

        Use this EXACT data path: {data_path}
        
        Follow this EXACT schema for the Pydantic model:
        {schema}

        Follow these exact patterns:

        1. Service Class Structure:
        ```python
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

        2. Must end with this exact pattern:
        ```python
        def start_service_name():
            service = ServiceName()
            service.run()

        if __name__ == "__main__":
            start_service_name()
        ```

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
            5. Handle data loading errors"""
        else:
            data_path = "data/specific_data.json"
            schema = "{}"
            json_instructions = ""

        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        ).format(json_data_info=json.dumps(json_data_info, indent=2) if json_data_info else "None")
        
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
            data_path=data_path,
            schema=schema
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