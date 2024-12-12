import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
# from codeqwen import CodeQwenLLM

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPEN_AI_MODEL")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
llm = ChatOpenAI(
    model='deepseek-chat', 
    openai_api_key=DEEPSEEK_API_KEY, 
    openai_api_base='https://api.deepseek.com',
)

resp = llm.invoke("Hi")
print(resp.content)