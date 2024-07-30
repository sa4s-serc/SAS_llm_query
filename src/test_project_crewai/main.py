#!/usr/bin/env python
import sys
from test_project_crewai.crew import FibonacciCrew


def run():
    """
    Run the crew.
    """
    # task_description = input(
    #     "Enter the task description (e.g., Write a Python function to calculate the nth Fibonacci number): "
    # )
    task_description = "Calclulate the n'th fibbonaci number"

    crew = FibonacciCrew()
    result = crew.kickoff(task_description=task_description)
    print(result)


if __name__ == "__main__":
    run()
