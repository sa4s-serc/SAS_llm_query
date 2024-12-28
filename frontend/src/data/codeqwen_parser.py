import os
import json
import re
from typing import Dict, List

def parse_single_file(file_path: str) -> Dict:
    """Parse a single conversation file and extract required components"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Initialize result structure
    result = {
        "conversation": [],
        "service_tracking": [],
        "original_goal": "",
        "core_services": "",
        "final_summary": ""
    }

    # Extract conversation and service tracking
    conv_section = re.search(r"Conversation with Service Tracking:\n(.*?)\nFinal Plan Summary:", 
                           content, re.DOTALL)
    if conv_section:
        conv_text = conv_section.group(1).strip()
        # Split into messages and service tracking
        messages = []
        current_message = []
        current_role = None
        
        for line in conv_text.split('\n'):
            if line.strip() == "Tourist:" or line.strip() == "Guide:":
                if current_role and current_message:
                    messages.append({
                        "role": current_role,
                        "content": "\n".join(current_message).strip()
                    })
                current_role = line.strip()[:-1]  # Remove the colon
                current_message = []
            elif line.startswith("Identified Services after Turn"):
                if current_role and current_message:
                    messages.append({
                        "role": current_role,
                        "content": "\n".join(current_message).strip()
                    })
                    current_message = []
                result["service_tracking"].append(line.strip())
            else:
                current_message.append(line)
        
        if current_role and current_message:
            messages.append({
                "role": current_role,
                "content": "\n".join(current_message).strip()
            })
        
        result["conversation"] = messages

    # Extract original goal
    goal_match = re.search(r"Original Goal: (.*?)\n", content)
    if goal_match:
        result["original_goal"] = goal_match.group(1).strip()

    # Extract core services and parameters
    services_section = re.search(r"Core Services and Parameters:\n(.*?)$", 
                               content, re.DOTALL)
    if services_section:
        result["core_services"] = services_section.group(1).strip()

    # Extract final summary
    summary_section = re.search(r"Final Plan Summary:\n(.*?)\nOriginal Goal:", 
                              content, re.DOTALL)
    if summary_section:
        result["final_summary"] = summary_section.group(1).strip()

    return result

def process_directory(dir_path: str, model_name: str) -> None:
    """Process all files in directory and create consolidated JSON"""
    all_conversations = []
    
    # Get all .txt files
    files = [f for f in os.listdir(dir_path) if f.endswith('.txt')]
    
    # Sort files numerically
    files.sort(key=lambda x: int(x.split('.')[0]))
    
    for file_name in files:
        file_path = os.path.join(dir_path, file_name)
        try:
            conversation_data = parse_single_file(file_path)
            conversation_data["id"] = file_name.split('.')[0]  # Add ID from filename
            all_conversations.append(conversation_data)
        except Exception as e:
            print(f"Error processing {file_name}: {str(e)}")
    
    # Write consolidated JSON
    output_file = f"data_{model_name}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({"model": model_name, "conversations": all_conversations}, 
                 f, indent=2, ensure_ascii=False)

    print(f"Processed {len(all_conversations)} files into {output_file}")


dir_path = "/home/bassam/Documents/research/code/goal_parser/runs/codeqwen"
model_name = "codeqwen"
process_directory(dir_path, model_name)