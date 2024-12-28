from typing import Any, List, Optional, Dict
from gradio_client import Client
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from crewai import Agent
import os
import sys
import random
import argparse
from pathlib import Path
import time
from dotenv import load_dotenv
from utils import load_microservices, get_user_goal, load_summary, load_service_parameters, write_output

# Initialize shared client
shared_client = None

def initialize_shared_client():
    global shared_client
    if shared_client is None:
        hf_token = os.environ.get("HF_TOKEN")
        shared_client = Client("bassamadnan/qwen", hf_token=hf_token)
    return shared_client

class CodeQwenAgent:
    """Custom agent implementation that directly uses Gradio client"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.client = initialize_shared_client()
        
    def execute_task(self, task_description: str, context: str = "") -> str:
        """Execute a task using the Qwen model"""
        prompt = f"""Role: {self.role}
Goal: {self.goal}
Background: {self.backstory}

Context: {context}

Task: {task_description}

Please provide your response:"""

        try:
            response = self.client.predict(
                prompt,
                api_name="/predict"
            )
            return response
        except Exception as e:
            print(f"Error executing task: {e}")
            return f"Error: {str(e)}"

class CustomTask:
    """Task class to maintain consistency with original implementation"""
    def __init__(self, description: str, agent: CodeQwenAgent, task_type: str = "conversation"):
        self.description = description
        self.agent = agent
        self.task_type = task_type
        self.output = None

class CustomCrew:
    """Enhanced crew implementation with service tracking"""
    
    def __init__(self, agents: List[CodeQwenAgent], tasks: List[Dict], user_goal: str, microservices: List[Dict], params_context: str):
        self.agents = agents
        self.tasks = tasks
        self.conversation_history = []
        self.identified_services = set()
        self.user_goal = user_goal
        self.microservices = microservices
        self.params_context = params_context
        
    def identify_services(self, conversation: str) -> str:
        """Identify relevant services from conversation"""
        prompt = f"""Based on the following conversation, identify the most relevant services from: {', '.join([ms['name'] for ms in self.microservices])}

Conversation:
{conversation}

Return only the service names as a comma-separated list."""
        
        return self.agents[1].execute_task(prompt)  # Using guide agent
        
    def generate_summary(self) -> str:
        """Generate final plan summary"""
        prompt = f"""Based on the conversation history, create a focused summary of the tourist's plan.
Include only places and activities that were specifically discussed.
Start with 'Based on our discussion, your plan includes...'

Conversation:
{chr(10).join(self.conversation_history)}"""
        
        return self.agents[1].execute_task(prompt)
        
    def format_service_parameters(self) -> str:
        """Format final service parameters"""
        prompt = f"""Based on the conversation history and the original goal: {self.user_goal}
List the most relevant services and their parameters.

Format your response EXACTLY like this example:
restaurant_finder:
- cuisine_type: [south indian, hyderabadi]
- dietary_restrictions: [vegetarian]

Available parameters:
{self.params_context}

Conversation:
{chr(10).join(self.conversation_history)}"""
        
        return self.agents[1].execute_task(prompt)
    
    def kickoff(self) -> Dict[str, Any]:
        """Execute all tasks with service tracking"""
        results = []
        service_tracking = []
        context = ""
        
        # Main conversation
        for i, task in enumerate(self.tasks):
            agent = self.agents[task['agent_index']]
            result = agent.execute_task(task['description'], context)
            
            # Update conversation history
            self.conversation_history.append(f"{agent.role}: {result}")
            results.append(result)
            
            # Identify services after guide responses
            if task['agent_index'] == 1:  # Guide's turn
                services = self.identify_services("\n".join(self.conversation_history))
                service_tracking.append(services)
                self.identified_services.update(services.split(", "))
            
            # Update context
            context = "Previous conversation:\n" + "\n".join(self.conversation_history)
        
        # Generate final outputs
        final_summary = self.generate_summary()
        service_params = self.format_service_parameters()
        
        return {
            "conversation": list(zip(range(len(results)), results)),
            "service_tracking": service_tracking,
            "final_summary": final_summary,
            "original_goal": self.user_goal,
            "service_parameters": service_params
        }

def setup_args():
    parser = argparse.ArgumentParser(description='Run CodeQwen simulations with custom index range')
    parser.add_argument('--start', type=int, default=1, help='Starting index for simulations (default: 1)')
    parser.add_argument('--end', type=int, default=100, help='Ending index for simulations (default: 100)')
    parser.add_argument('--output-dir', type=str, default='runs/codeqwen2', help='Output directory (default: runs/codeqwen2)')
    parser.add_argument('--wait-time', type=int, default=5, help='Wait time between simulations in seconds (default: 5)')
    return parser.parse_args()

def ensure_output_directory(directory: str) -> None:
    Path(directory).mkdir(parents=True, exist_ok=True)

def create_tasks(max_turns: int, user_goal: str, available_hours: int) -> List[Dict]:
    tasks = []
    for turn in range(max_turns * 2):
        agent_index = 0 if turn % 2 == 0 else 1
        
        if turn % 2 == 0:  # Tourist's turn
            if turn == 0:
                description = f"""Start the conversation naturally:
                - Express your main interest: {user_goal}
                - Ask about specific types of local experiences
                - Mention your {available_hours} hour time constraint"""
            elif turn == 2:
                description = """Based on the guide's suggestions:
                - Show interest in one or two mentioned places
                - Ask specific questions about those places
                - Express any particular preferences"""
            else:
                description = """For your final response:
                - Confirm interest in the suggested itinerary
                - Ask any final questions about timing or logistics
                - Show enthusiasm about the planned activities"""
        else:  # Guide's turn
            if turn == 1:
                description = f"""Provide a focused initial response:
                - Suggest 2-3 specific places that match their interests
                - Stay true to their desire for {user_goal}
                - Ask about specific preferences
                Keep suggestions limited and focused."""
            elif turn == 3:
                description = """Build upon your previous suggestions:
                - Add details about previously mentioned places
                - Suggest 1-2 complementary activities nearby
                - Maintain consistency with earlier recommendations"""
            else:
                description = """Provide a final focused response:
                - Give specific timing for mentioned activities
                - Stick to previously suggested locations
                - Add any essential final details"""
        
        tasks.append({
            'agent_index': agent_index,
            'description': description
        })
    
    return tasks

def run_simulation(index: int, output_dir: str) -> tuple[bool, float]:
    output_file = os.path.join(output_dir, f"{index}.txt")
    start_time = time.time()
    
    try:
        # Load environment variables
        load_dotenv()
        max_turns = 3

        # Load all required files
        MICROSERVICES_FILE = "services.txt"
        SUMMARY_FILE = "summary.txt"
        PARAMS_FILE = "service_params.txt"

        microservices = load_microservices(MICROSERVICES_FILE)
        system_summary = load_summary(SUMMARY_FILE)
        params_list = load_service_parameters(PARAMS_FILE)

        # Format parameters for agent context
        params_context = "\n".join([
            f"Service '{service}' options: " + 
            ", ".join([f"{param}: {', '.join(values)}" for param, values in params.items()])
            for service, params in params_list.items()
        ])

        # Get user goal and time constraint
        user_goal = get_user_goal()
        available_hours = random.randint(2, 5)

        # Create agents (will use shared client)
        tourist = CodeQwenAgent(
            role="Hyderabad Tourist",
            goal=f"To explore Hyderabad and {user_goal} within {available_hours} hours",
            backstory=f"""You are a tourist visiting Hyderabad with {available_hours} hours to spare. 
            Your main interest is: {user_goal}. 
            You want to learn about the area and make the most of your time.
            You communicate naturally and ask relevant follow-up questions."""
        )
        
        guide = CodeQwenAgent(
            role="Hyderabad City Guide",
            goal="To assist tourists efficiently while maintaining consistency in recommendations",
            backstory=f"""You are a knowledgeable guide for Hyderabad, helping tourists plan their visit. 
            {system_summary}
            
            Available service options:
            {params_context}
            
            Important guidelines:
            1. Suggest only 2-3 locations/activities per response
            2. Stay consistent with your recommendations throughout
            3. Keep the original goal in mind when making suggestions
            4. Consider time constraints when planning"""
        )

        # Create tasks
        tasks = create_tasks(max_turns, user_goal, available_hours)
        
        # Create crew and run conversation
        crew = CustomCrew(
            agents=[tourist, guide],
            tasks=tasks,
            user_goal=user_goal,
            microservices=microservices,
            params_context=params_context
        )
        
        results = crew.kickoff()
        end_time = time.time()
        time_taken = end_time - start_time

        # Add timing and index to results before writing
        results['simulation_time'] = time_taken
        results['simulation_index'] = index
        results['available_hours'] = available_hours
        results['user_goal'] = user_goal
        
        write_output(results, output_file)
        return True, time_taken

    except Exception as e:
        end_time = time.time()
        time_taken = end_time - start_time
        print(f"Error in simulation {index}: {str(e)}")
        
        # Try to write error information to the output file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"Simulation Index: {index}\n")
                f.write(f"Time taken: {time_taken:.2f} seconds\n")
                f.write(f"Error occurred: {str(e)}\n")
        except:
            pass
            
        return False, time_taken

def main():
    # Initialize the shared client at the start
    print("Initializing CodeQwen model...")
    initialize_shared_client()
    
    args = setup_args()
    ensure_output_directory(args.output_dir)
    
    total_sims = args.end - args.start + 1
    successful = 0
    failed = 0
    total_time = 0
    
    print(f"Starting simulations from {args.start} to {args.end}")
    print(f"Output directory: {args.output_dir}")
    print("----------------------------------------")
    
    for i in range(args.start, args.end + 1):
        print(f"Running simulation {i} of {args.end}...")
        
        success, time_taken = run_simulation(i, args.output_dir)
        total_time += time_taken
        
        print(f"Time taken for simulation {i}: {time_taken:.2f} seconds")
        
        if success:
            successful += 1
            print(f"Simulation {i} completed successfully")
        else:
            failed += 1
            print(f"Simulation {i} failed")
        
        if i < args.end:
            print(f"Waiting for {args.wait_time} seconds before next simulation...")
            time.sleep(args.wait_time)
        
        print("----------------------------------------")
    
    print("\nSimulation Summary:")
    print(f"Total simulations: {total_sims}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Total time taken: {total_time:.2f} seconds")
    print(f"Average time per simulation: {(total_time/total_sims):.2f} seconds")
    print("All simulations completed!")

if __name__ == "__main__":
    main()