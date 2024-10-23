GENERATED_APP_TEMPLATE = """
import os
import sys
import streamlit as st
import requests
import logging
import json
from utils.port_manager import get_port_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the working directory to the app directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="My IIIT Companion", page_icon="🏫", layout="wide")

st.title("My IIIT Companion")

port_manager = get_port_manager()

def render_numeric_data(key, value):
    st.metric(label=key.capitalize(), value=value)

def render_list_data(key, value):
    st.subheader(key.capitalize())
    for item in value:
        if isinstance(item, dict):
            with st.expander(item.get('name', 'Item')):
                for k, v in item.items():
                    if k != 'name':
                        st.write(f"**{{k.capitalize()}}:** {{v}}")
        else:
            st.info(item)

def render_dict_data(key, value):
    st.subheader(key.capitalize())
    if all(isinstance(v, (int, float)) for v in value.values()):
        st.bar_chart(value)
    else:
        for k, v in value.items():
            st.write(f"**{{k}}:** {{v}}")

def render_service_data(service_name, data):
    for key, value in data.items():
        if isinstance(value, (int, float)):
            render_numeric_data(key, value)
        elif isinstance(value, list):
            render_list_data(key, value)
        elif isinstance(value, dict):
            render_dict_data(key, value)
        else:
            st.write(f"**{{key}}:** {{value}}")

{services}

{debug_content}
"""
