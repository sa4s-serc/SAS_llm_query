import os
import random
from typing import List
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure that the OpenAI API key is set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPEN_AI_MODEL = os.getenv("OPEN_AI_MODEL")

if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

def initialize_chat_model():
    return ChatOpenAI(openai_api_key=OPENAI_API_KEY, temperature=0.7, model_name=OPEN_AI_MODEL)

def get_user_goal() -> str:
    user_prompts = [
        "I need a quiet workspace to concentrate on my project. Air quality is somewhat important, but temperature is not a major concern.",
        "Can you help me find a space with strong Wi-Fi and multiple charging stations? I'll be working on some presentations.",
        "I'm looking to book a collaborative area with large displays for team meetings. It should be available right now.",
        "I prefer a comfortable temperature and natural light to stay inspired. Noise isn't a big issue for me.",
        "I need a workspace immediately that has access to interactive displays and fast internet.",
        "I'm planning an event and need a space that can accommodate a larger group with tech-enabled features like microphones.",
        "I'd like to explore new areas that are good for team collaboration with interesting design features.",
        "Please show me available spaces with good ventilation and comfortable seating.",
        "I don't mind if the space is busy. I'm here to explore and maybe meet others.",
        "I'd prefer a quieter area with fewer distractions, as I need to focus on my work."
    ]
    return random.choice(user_prompts)

def create_system_message(goal: str) -> SystemMessage:
    return SystemMessage(content=f"""
    You are an AI agent simulating a visitor to a smart city event. Your goal is: {goal}
    
    Engage in a natural conversation with the event chatbot (played by a human). Ask questions 
    that will help you achieve your goal. Be curious, specific, and maintain a human-like 
    conversation flow. Don't reveal that you're an AI or mention your goal directly.
    
    After each response from the chatbot, decide if you have enough information to achieve your goal.
    If you do, or if the chatbot seems to have provided all relevant information, thank them and end the conversation.
    
    If you need more information, ask a follow-up question or make a relevant comment to keep the conversation going.
    
    Remember:
    1. Stay focused on your goal
    2. Ask natural, conversational questions
    3. Respond to the chatbot's answers appropriately
    4. Be willing to end the conversation when you have sufficient information
    5. If the chatbot asks if they've addressed your needs, answer honestly based on your goal
    """)

def main():
    llm = initialize_chat_model()
    user_goal = get_user_goal()
    print(f"Visitor's goal: {user_goal}\n")

    conversation = [create_system_message(user_goal)]
    turn_count = 0

    while True:
        # Get the AI visitor's message
        visitor_message = llm(conversation + [HumanMessage(content="Visitor: (Respond to the chatbot. If you have enough information or the chatbot has indicated they've provided all relevant details, thank them and end the conversation. Otherwise, ask a follow-up question.)")])
        print(f"Visitor: {visitor_message.content}")
        conversation.append(visitor_message)

        # Check if the visitor wants to end the conversation
        if "thank you" in visitor_message.content.lower() and any(phrase in visitor_message.content.lower() for phrase in ["goodbye", "bye", "end", "conclude"]):
            break

        # Get the human's response (simulating the chatbot)
        chatbot_response = input("Chatbot: ")
        conversation.append(HumanMessage(content=chatbot_response))

        turn_count += 1

        # Additional check to potentially end the conversation
        if turn_count >= 3:
            end_conversation = llm([SystemMessage(content="Based on the conversation so far and your goal, decide if you have enough information to conclude the conversation. Respond with only 'yes' or 'no'.")] + conversation)
            if end_conversation.content.lower().strip() == 'yes':
                print("\nVisitor: Thank you for all the information. I think I have what I need now. Goodbye!")
                break

    print("\nConversation concluded.")

if __name__ == "__main__":
    main()