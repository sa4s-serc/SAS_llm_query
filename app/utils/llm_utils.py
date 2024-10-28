import random
from typing import List, Dict

def get_user_goal() -> str:
    user_prompts = [
        # Historical Sites & Museums
        "I'd love to visit Charminar and understand its history. Wonder if it gets too crowded on weekends?",
        "The Golconda Fort sounds fascinating! I'd like to explore it thoroughly. What's the best way to get there?",
        "I'm really interested in visiting Salar Jung Museum. Do they have any special exhibitions going on?",
        
        # Water Bodies & Parks
        "I'm thinking of spending some time near Hussain Sagar Lake. How clean is the water there?",
        "Would love to visit Durgam Cheruvu for a peaceful evening. Is the area nice for walking?",
        
        # Shopping & Markets
        "I want to explore Laad Bazaar for traditional bangles. What's the best way to reach there?",
        "Planning to visit GVK One for some shopping. Is it usually very crowded on weekdays?",
        
        # Food & Dining
        "Craving some authentic Hyderabadi biryani! Any vegetarian-friendly places you'd recommend?",
        "Looking for a good place serving traditional Irani chai and Osmania biscuits!",
        
        # Cultural Events & Exhibitions
        "Are there any cultural exhibitions happening in the city? Particularly interested in traditional art.",
        "Would love to see some local handicraft exhibitions. Anything interesting coming up?"
    ]
    return random.choice(user_prompts)

def load_microservices(file_path: str) -> List[Dict[str, str]]:
    microservices = []
    with open(file_path, "r") as f:
        for line in f:
            if line.strip():
                try:
                    name, description = line.strip().split(",", 1)
                    microservices.append({"name": name.strip(), "description": description.strip()})
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    return microservices

def load_summary(file_path: str) -> str:
    try:
        with open(file_path, "r") as f:
            summary = f.read().strip()
        return summary
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return ""
    except IOError:
        print(f"Error: Unable to read file at {file_path}")
        return ""

def load_service_parameters(file_path: str) -> dict:
    service_params = {}
    try:
        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                service_param, values = line.split('=')
                service_name, param_name = service_param.split('.')
                if service_name not in service_params:
                    service_params[service_name] = {}
                value_list = [v.strip() for v in values.split(',')]
                service_params[service_name][param_name] = value_list
        return service_params
    except FileNotFoundError:
        print(f"Error: Parameter file not found at {file_path}")
        return {}
    except Exception as e:
        print(f"Error loading parameters: {str(e)}")
        return {}
