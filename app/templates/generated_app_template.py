# TODO: set up app name from config
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

st.set_page_config(page_title="My City Companion", page_icon="🏫", layout="wide")

st.title("My City Companion")

port_manager = get_port_manager()

def render_metric_card(header, value, description=None):
    st.markdown(
        f'''
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;">
            <h4>{{header}}</h4>
            <h2>{{value}}</h2>
            {{"<p>" + description + "</p>" if description else ""}}
        </div>
        ''',
        unsafe_allow_html=True
    )

def render_info_card(header, content):
    st.markdown(
        f'''
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;">
            <h4>{{header}}</h4>
            <p>{{content}}</p>
        </div>
        ''',
        unsafe_allow_html=True
    )

def render_numeric_data(key, value):
    if isinstance(value, (int, float)):
        render_metric_card(key.replace('_', ' ').title(), value)
    else:
        render_info_card(key.replace('_', ' ').title(), value)

def render_list_data(key, value):
    st.markdown(f"### {{key.replace('_', ' ').title()}}")
    
    if not value:
        st.info("No items to display.")
        return

    cols = st.columns(3)
    for idx, item in enumerate(value):
        with cols[idx % 3]:
            if isinstance(item, dict):
                st.markdown("---")
                if 'name' in item:
                    st.markdown(f"**{{item['name']}}**")
                elif 'event_name' in item:
                    st.markdown(f"**{{item['event_name']}}**")
                elif 'location' in item:
                    st.markdown(f"**{{item['location']}}**")
                
                for k, v in item.items():
                    if k not in ['name', 'event_name', 'location']:
                        if isinstance(v, (int, float)):
                            st.metric(k.replace('_', ' ').title(), v)
                        else:
                            st.write(f"**{{k.replace('_', ' ').title()}}:** {{v}}")
            else:
                st.markdown(f"- {{item}}")

def render_dict_data(key, value):
    st.markdown(f"### {{key.replace('_', ' ').title()}}")
    
    if all(isinstance(v, (int, float)) for v in value.values()):
        cols = st.columns(len(value))
        for col, (k, v) in zip(cols, value.items()):
            col.metric(label=k.replace('_', ' ').title(), value=v)
    else:
        cols = st.columns(3)
        for idx, (k, v) in enumerate(value.items()):
            with cols[idx % 3]:
                if isinstance(v, (int, float)):
                    st.metric(k.replace('_', ' ').title(), v)
                else:
                    st.markdown(f"**{{k.replace('_', ' ').title()}}:** {{v}}")

def render_service_data(service_name, data):
    st.markdown(f"## {{service_name.replace('_', ' ').title()}}")
    
    if "message" in data:
        st.info(data["message"])
    
    for key, value in data.items():
        if key == "message":
            continue
        if isinstance(value, (int, float)):
            render_numeric_data(key, value)
        elif isinstance(value, list):
            render_list_data(key, value)
        elif isinstance(value, dict):
            render_dict_data(key, value)
        else:
            st.write(f"**{{key.replace('_', ' ').title()}}:** {{value}}")
    
    st.markdown("---")

{services}

{debug_content}
"""
