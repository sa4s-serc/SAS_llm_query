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
API_KEY = os.getenv("OPEN_AI_API_KEY")
MODEL = os.getenv("OPEN_AI_MODEL")

class QueryRefiner:
    def __init__(self, service_manager):
        self.service_manager = service_manager
        self.llm = ChatOpenAI(model_name=MODEL, temperature=0.7)

    def refine(self, query: str):
        (
            refined_query,
            needs_json_data,
            data_sources_needed,
            http_method,
        ) = self._refine_query(query)
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
            result = {
                "service_exists": False,
                "refined_query": refined_query,
                "suggested_port": suggested_port,
                "service_description": f"A service that {refined_query.lower()}",
                "needs_json_data": needs_json_data,
                "data_sources_needed": data_sources_needed,
                "http_method": http_method,
            }
            if needs_json_data:
                result["json_data_info"] = [
                    source
                    for source in self.service_manager.get_json_data_sources()
                    if source["name"] in data_sources_needed
                ]
            return result

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

        system_template = """You are an AI assistant specializing in matching user queries to existing services.
        Your task is to analyze the user's query and determine if any existing service can fulfill it."""

        human_template = """Given the following user query and list of existing service descriptions,
        determine if any existing service can fulfill the query. If a match is found, return the index of the matching service (0-based).
        If no match is found, return -1.

        User query: {query}

        Existing service descriptions:
        {services}

        {format_instructions}
        """

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        response = chain.run(
            query=query,
            services=json.dumps(services_descriptions, indent=2),
            format_instructions=format_instructions,
        )

        try:
            parsed_output = output_parser.parse(response)
            matching_index = int(parsed_output["matching_index"])
            print(f"parsed_output ---> {parsed_output} \n\n\n\n\n")
            if matching_index >= 0 and matching_index < len(self.service_manager.services):
                return self.service_manager.services[matching_index]
        except ValueError as e:
            print(f"Error parsing matching_index: {e}")
        except Exception as e:
            print(f"Error parsing LLM response for service matching: {e}")

        return None

    def _refine_query(self, query: str):
        system_template = """You are an AI assistant specializing in refining user queries into general requests for writing Python FastAPI services.
        Your task is to analyze the user's query and formulate a clear, specific request for a FastAPI service that addresses the general case of the query.

        IMPORTANT: Carefully examine if the query needs specific data types from the available JSON data sources. For example:
        - If query mentions restaurants, it needs "restaurant_data"
        - If query mentions air quality, it needs "air_quality_data"
        - If query mentions historical sites, it needs "historic_data"
        - If query mentions exhibitions, it needs "exhibition_data"
        - If query mentions events, it needs "event_data"
        - If query mentions crowd monitoring, it needs "crowd_data"
        - If query mentions water quality, it needs "water_quality_data"

        You have access to the following JSON data sources:
        {json_data_info}

        Determine if the query requires access to any JSON data sources. If it does, specify the exact data source name(s) needed from the list provided.
        Also, determine whether the query is more suitable for a GET or POST HTTP method.

        The goal is to create a service that matches the requirements and uses the correct data source(s).
        """

        human_template = """
        Original query: {query}

        Instructions:
        1. Analyze the query to understand what data source(s) it needs
        2. Formulate a clear and specific request for writing a FastAPI service
        3. Start your refined query with "Create a FastAPI service to" 
        4. Explicitly identify all required data sources from the provided list
        5. Determine the appropriate HTTP method (GET/POST)

        Output your response in the following format:
        Refined query: "Create a FastAPI service to..."
        Needs JSON data: [True/False]
        Data source(s) needed: [List of exact data source names, or "None" if no source is needed]
        HTTP Method: [GET/POST]
        """

        json_data_info = self.service_manager.get_json_data_sources()
        json_data_info_str = json.dumps(
            [
                {
                    "name": source["name"],
                    "description": source["description"],
                    "schema": source["schema"],
                }
                for source in json_data_info
            ],
            indent=2,
        )
        system_message_prompt = SystemMessagePromptTemplate.from_template(
            system_template
        ).format(json_data_info=json_data_info_str)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )

        chain = LLMChain(llm=self.llm, prompt=chat_prompt)
        result = chain.run(query=query)

        # Parse the result
        refined_query = (
            result.split("Refined query:")[1]
            .split("Needs JSON data:")[0]
            .strip()
            .strip('"')
        )
        needs_json_data = (
            result.split("Needs JSON data:")[1]
            .split("Data source(s) needed:")[0]
            .strip()
            .lower()
            == "true"
        )
        data_sources_needed = (
            result.split("Data source(s) needed:")[1]
            .split("HTTP Method:")[0]
            .strip()
            .strip("[]")
            .split(", ")
        )
        data_sources_needed = [
            source.strip("'\"")
            for source in data_sources_needed
            if source.strip("'\"").lower() != "none"
        ]
        http_method = result.split("HTTP Method:")[1].strip().upper()

        print("data sources needed--->", data_sources_needed)
        print("HTTP Method --->", http_method, "\n\n\n\n")
        return (
            refined_query,
            needs_json_data,
            data_sources_needed,
            http_method,
        )