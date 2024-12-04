from pathlib import Path

def load_prompt_template(filename: str, **kwargs) -> str:
    """
    Load a prompt template from the prompts directory and optionally format it.
    
    :param filename: Name of the prompt template file
    :param kwargs: Keyword arguments to format the template
    :return: Formatted prompt template string
    """
    prompts_dir = Path(__file__).parent / "prompts"
    prompt_path = prompts_dir / filename
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template {filename} not found in {prompts_dir}")
        
    with open(prompt_path, "r") as f:
        template = f.read()
    
    # If kwargs are provided, format the template
    if kwargs:
        template = template.format(**kwargs)
    
    return template