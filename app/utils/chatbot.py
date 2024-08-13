import streamlit as st
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts.prompt import PromptTemplate
from dotenv import load_dotenv
import os

load_dotenv()

# List of available keywords
available_keywords = [
    "environmental",
    "resource",
    "academic",
    "event",
    "health",
    "temperature",
    "humidity",
    "air quality",
    "library",
]


# Function to refine user query and get keywords
def chatbot(query):
    template = """You are a query refiner for the IIIT Companion app. You need to refine the user query to make it more specific and actionable.
    You need to understand the context of the query and provide key words that can help the app to generate the app according to user query.
    Now, analyze the sentence and provided keywords and give the list of appropriate keywords from the given list of keywords as output.
    List of keywords are environmental, resource, academic, event, health, temperature, humidity, air quality, library.
    If user's query is not clear, even after analyzing the context, you should ask for more information by asking "sorry, I didn't get that. Can you please provide more information?"
    for the following user question: {input}
    Current conversation:
    {history}
    If the user's input is unclear refer to conversation history and ask again for more clarity.
    These are the keywords which you can output according to user's query:
    Environmental: when user asks about air quality, temperature, humidity.When user asks about weather, pollution, climate.
    Resource: when user asks about library, cafeteria, study rooms.When user asks where he can study peacefully, where he can find books.
    Academic: when user asks about assignments, classes, grades.When user asks about courses, exams, syllabus, marks.
    Event: when user asks about campus events, clubs, workshops.When user says he is bored, he wants to join a club, he wants to attend a workshop. When user says he wants to have fun.
    Health: when user asks about wellness tips, fitness, mental health.When user says he is feeling low, he wants to be fit, he wants to be healthy.
    temperature: when user asks about temperature.
    humidity: when user asks about humidity.
    air quality: when user asks about air quality.
    library: when user asks about library."""

    # Replace with your actual OpenAI API key
    open_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(
        openai_api_key=open_api_key,
    )
    PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=llm,
        verbose=True,
        memory=ConversationBufferMemory(ai_prefix="AI Assistant"),
    )

    try:
        output = conversation.predict(input=query)
        # st.write(f"AI Assistant: {output}")
        if output is None:
            raise ValueError("Output from chain.invoke is None")

        # Check if the output contains a request for more information
        if "sorry" in output.lower():
            return output

        # Filter the output to include only the available keywords
        filtered_keywords = [
            keyword for keyword in available_keywords if keyword in output.lower()
        ]
        return filtered_keywords
    except Exception as e:
        return f"Error invoking chain: {e}"


# Function to log queries and results to CSV
def log_to_csv(user_query, refined_keywords):
    file_path = "query_logs.csv"

    # Check if file exists
    try:
        # If the file exists, load it
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # If the file does not exist, create a new DataFrame
        df = pd.DataFrame(columns=["User Query", "Refined Keywords"])

    # Create a DataFrame for the new data
    new_data = pd.DataFrame(
        {"User Query": [user_query], "Refined Keywords": [refined_keywords]}
    )

    # Concatenate new data to the existing DataFrame
    df = pd.concat([df, new_data], ignore_index=True)

    # Save back to CSV
    df.to_csv(file_path, index=False)


# Streamlit interface


def take_input(user_input):
    # user_input = st.chat_input("Enter a query")
    # Initialize Streamlit session state

    if user_input:
        with st.spinner("Processing..."):
            # history = "\n".join([f"User: {msg['user']}\nAI Assistant: {msg['ai']}" for msg in st.session_state.conversation])
            refined_query = chatbot(user_input)
            print(refined_query)
            # Append current query and response to conversation history
            st.session_state.conversation.append(
                {"user": user_input, "ai": refined_query}
            )
            # for msg in st.session_state.conversation:
            #     with st.chat_message("user"):
            #         response = st.markdown(msg['user'])
            #     with st.chat_message("assistant"):
            #         response = st.markdown(msg['ai'])
            # Log the user query and refined keywords to CSV
            log_to_csv(user_input, refined_query)
            if isinstance(refined_query, list):
                print(refined_query)
                return refined_query
            else:
                st.write(refined_query)
