from typing import Any, List, Optional, Dict
from gradio_client import Client
from typing import Any, List, Optional, Dict
from langchain.llms.base import LLM
from langchain.callbacks.manager import CallbackManagerForLLMRun
from gradio_client import Client
from crewai import Agent  
import os

class CodeQwenAgent:
    """Custom agent implementation that directly uses Gradio client"""
    
    def __init__(self, role: str, goal: str, backstory: str):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.hf_token = os.environ.get("HF_TOKEN")
        self.client = Client("bassamadnan/qwen", hf_token=self.hf_token)
        
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

class CodeQwenLLM(LLM):
    """Custom LLM class for CodeQwen that works with CrewAI"""
    
    hf_token: Optional[str] = None
    client: Optional[Client] = None
    
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hf_token = os.environ.get("HF_TOKEN")
        self.client = Client("bassamadnan/qwen", hf_token=self.hf_token)
    
    @property
    def _llm_type(self) -> str:
        return "custom_qwen"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Execute the LLM call."""
        if self.client is None:
            raise ValueError("Client not initialized")
        
        response = self.client.predict(
            prompt,
            api_name="/predict"
        )
        return response

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {"name": "CodeQwen1.5-7B-Chat"}

def write_output(results: Dict[str, Any], output_file: str):
    """Write formatted output to file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write conversation with service tracking
        f.write("\nConversation with Service Tracking:\n")
        service_index = 0
        for i, (_, message) in enumerate(results["conversation"]):
            role = "Tourist" if i % 2 == 0 else "Guide"
            f.write(f"\n{role}:\n{message}\n")
            if role == "Guide":
                f.write(f"\nIdentified Services after Turn {service_index + 1}:\n")
                f.write(results["service_tracking"][service_index])
                f.write("\n")
                service_index += 1

        # Write final summary and services
        f.write("\nFinal Plan Summary:\n")
        f.write(results["final_summary"])
        f.write("\n")

        f.write("\nOriginal Goal: ")
        f.write(results["original_goal"])
        f.write("\n")

        f.write("\nCore Services and Parameters:\n")
        f.write(results["service_parameters"])
        f.write("\n")

"""
def main(output_file):
    # Create agents
    tourist = CodeQwenAgent(...)
    guide = CodeQwenAgent(...)
    
    # Create tasks
    tasks = [...]
    
    # Create crew
    crew = CustomCrew(
        agents=[tourist, guide],
        tasks=tasks,
        user_goal=user_goal,
        microservices=microservices,
        params_context=params_context
    )
    
    # Run conversation
    results = crew.kickoff()
    
    # Write output
    write_output(results, output_file)
"""