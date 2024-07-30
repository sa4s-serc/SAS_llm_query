from crewai import Agent, Crew, Task
from crewai.project import CrewBase, agent, crew, task
import sys


@CrewBase
class FibonacciCrew:
    """Crew for refining prompts and generating functions based on user input"""

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

    @task
    def refine_prompt_task(self) -> Task:
        return Task(
            description="Refine the user's task description into a clear and specific prompt for function generation",
            expected_output="A refined and specific prompt for generating a Python function",
            agent=self.prompt_refiner(),
        )

    @task
    def generate_function_task(self) -> Task:
        return Task(
            description="Generate a Python function based on the refined prompt",
            expected_output="A Python function that solves the given problem",
            agent=self.function_generator(),
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.prompt_refiner(), self.function_generator()],
            tasks=[self.refine_prompt_task(), self.generate_function_task()],
            verbose=2,
        )

    def kickoff(self, task_description: str):
        # Update the initial task description
        self.crew().tasks[
            0
        ].description = (
            f"Refine this task description into a clear prompt: {task_description}"
        )

        # Execute the crew
        result = self.crew().kickoff()

        print("Final Result:")
        print(result)
        sys.exit(0)  # Exit the program after completion
