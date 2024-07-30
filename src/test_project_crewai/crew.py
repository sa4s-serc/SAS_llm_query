from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
from typing import Dict, List


@CrewBase
class FunctionCrewServer:
    def __init__(self):
        self.function_registry: Dict[str, str] = {}

    @agent
    def query_agent(self) -> Agent:
        return Agent(
            role="Query Handler",
            goal="Process incoming queries and manage function registry",
            backstory="You are responsible for handling client requests and managing the function registry.",
            verbose=True,
        )

    @agent
    def prompt_refiner(self) -> Agent:
        return Agent(
            role="Prompt Refinement Specialist",
            goal="Refine user inputs into clear, specific prompts for function generation",
            backstory="You are an expert in crafting precise and effective prompts for coding tasks.",
            verbose=True,
        )

    @agent
    def function_generator(self) -> Agent:
        return Agent(
            role="Python Function Generator",
            goal="Generate efficient Python functions based on refined prompts",
            backstory="You are a skilled Python developer known for writing clean, efficient, and well-documented code.",
            verbose=True,
        )

    def handle_query_task(self, query: str) -> Task:
        return Task(
            description=f"Process this query: {query}. Check if a function exists in the registry or if a new one needs to be generated.",
            expected_output="Either the result of an existing function or a request for a new function",
            agent=self.query_agent(),
        )

    def refine_prompt_task(self) -> Task:
        return Task(
            description="Refine the user's task description into a clear and specific prompt for function generation",
            expected_output="A refined and specific prompt for generating a Python function",
            agent=self.prompt_refiner(),
        )

    def generate_function_task(self) -> Task:
        return Task(
            description="Generate a Python function based on the refined prompt",
            expected_output="A Python function that solves the given problem",
            agent=self.function_generator(),
        )

    def create_crew(self, query: str) -> Crew:
        tasks = [
            self.handle_query_task(query),
            self.refine_prompt_task(),
            self.generate_function_task(),
        ]
        return Crew(
            agents=[
                self.query_agent(),
                self.prompt_refiner(),
                self.function_generator(),
            ],
            tasks=tasks,
            verbose=2,
        )

    def process_query(self, query: str):
        crew_instance = self.create_crew(query)

        # Execute the crew
        result = crew_instance.kickoff()

        # Convert CrewOutput to a string
        if hasattr(result, "content"):
            result_str = str(result.content)
        else:
            result_str = str(result)

        # Here you would parse the result and update the function registry if a new function was generated
        if "def " in result_str:  # This is a new function
            function_name = result_str.split("def ")[1].split("(")[0]
            self.function_registry[function_name] = result_str

        return result_str
