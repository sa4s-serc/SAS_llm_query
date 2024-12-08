import os
import sys
import streamlit as st

# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

from app.utils.service_manager import render_service_manager

st.set_page_config(
    page_title="Service Manager",
    page_icon="🔧",
    layout="wide"
)

render_service_manager() 