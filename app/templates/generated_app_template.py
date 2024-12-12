# TODO: set up app name from config
GENERATED_APP_TEMPLATE = """
import os
import sys
import streamlit as st
import requests
import logging
import json
from utils.port_manager import get_port_manager
from utils.feedback_collector import FeedbackCollector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Set the working directory to the app directory
app_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(app_dir)

# Get root directory (two levels up from app directory)
root_dir = os.path.dirname(os.path.dirname(app_dir))

# Load app data
with open('app_data.json', 'r') as f:
    app_data = json.load(f)
    conversation_history = app_data.get('conversation_history', [])
    selected_services = app_data.get('selected_services', [])
    service_parameters = app_data.get('parameters', {})

st.set_page_config(page_title="My City Companion", page_icon="🏫", layout="wide")

# Initialize feedback collector with root data directory
feedback_collector = FeedbackCollector(feedback_dir=os.path.join(root_dir, "data"))

# Sidebar Feedback Form
st.sidebar.title("Share Your Feedback")
st.sidebar.write("Help us improve your experience!")

user_name = st.sidebar.text_input(
    "Enter your name",
    help="Optional: Your name will help us better understand our users",
    key="feedback_name"
)

query_summary = st.sidebar.text_area(
    "Briefly summarize about the queries you have asked",
    help="This helps us understand how users interact with our system",
    key="query_summary"
)

app_rating = st.sidebar.slider(
    "Rate the application on a scale of 1 to 5",
    min_value=1,
    max_value=5,
    value=3,
    help="1 = Poor, 5 = Excellent",
    key="app_rating"
)

accuracy = st.sidebar.slider(
    "How accurate were the selected services for your needs?",
    min_value=1,
    max_value=5,
    value=3,
    help="1 = Not accurate at all, 5 = Extremely accurate",
    key="accuracy_rating"
)

relevance = st.sidebar.slider(
    "How relevant were the selected services to your query?",
    min_value=1,
    max_value=5,
    value=3,
    help="1 = Not relevant at all, 5 = Extremely relevant",
    key="relevance_rating"
)

missing = st.sidebar.multiselect(
    "Were there any services you expected but weren't selected?",
    options=get_port_manager().get_all_services(),
    default=[],
    key="missing_services"
)

unnecessary = st.sidebar.multiselect(
    "Were any of the selected services unnecessary?",
    options=selected_services,
    default=[],
    key="unnecessary_services"
)

overall_experience = st.sidebar.text_area(
    "How is your overall experience?",
    help="Please share your thoughts about using the application",
    key="overall_experience"
)

other_suggestions = st.sidebar.text_area(
    "Other suggestions / feedback",
    help="Any additional ideas or comments to help us improve",
    key="other_suggestions"
)

would_use_again = st.sidebar.checkbox(
    "Would you use this system again?",
    value=True,
    key="would_use_again"
)

if st.sidebar.button("Submit Feedback", key="submit_feedback"):
    feedback_data = {
        "user_name": user_name,
        "conversation_history": conversation_history,
        "query_summary": query_summary,
        "app_rating": app_rating,
        "selected_services": selected_services,
        "accuracy_rating": accuracy,
        "relevance_rating": relevance,
        "missing_services": missing,
        "unnecessary_services": unnecessary,
        "overall_experience": overall_experience,
        "other_suggestions": other_suggestions,
        "would_use_again": would_use_again
    }

    if feedback_collector.save_feedback(feedback_data):
        st.sidebar.success("Thank you for your feedback! 🙏")
    else:
        st.sidebar.error("Sorry, there was an error saving your feedback. Please try again.")

st.title("My City Companion")

port_manager = get_port_manager()

def render_metric_card(header, value, description=None):
    st.markdown(
        '''
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;">
            <h4>{header}</h4>
            <h2>{value}</h2>
            {"<p>" + description + "</p>" if description else ""}
        </div>
        '''.format(header=header, value=value, description=description),
        unsafe_allow_html=True
    )

def render_info_card(header, content):
    st.markdown(
        '''
        <div style="padding: 1rem; border-radius: 0.5rem; background-color: #f0f2f6; margin-bottom: 1rem;">
            <h4>{header}</h4>
            <p>{content}</p>
        </div>
        '''.format(header=header, content=content),
        unsafe_allow_html=True
    )

def render_numeric_data(key, value):
    if isinstance(value, (int, float)):
        render_metric_card(key.replace('_', ' ').title(), value)
    else:
        render_info_card(key.replace('_', ' ').title(), value)

def render_list_data(key, value):
    st.markdown("### " + key.replace('_', ' ').title())
    
    if not value:
        st.info("No items to display.")
        return

    cols = st.columns(3)
    for idx, item in enumerate(value):
        with cols[idx % 3]:
            if isinstance(item, dict):
                st.markdown("---")
                if 'name' in item:
                    st.markdown("**" + str(item['name']) + "**")
                elif 'event_name' in item:
                    st.markdown("**" + str(item['event_name']) + "**")
                elif 'location' in item:
                    st.markdown("**" + str(item['location']) + "**")
                
                for k, v in item.items():
                    if k not in ['name', 'event_name', 'location']:
                        if isinstance(v, (int, float)):
                            st.metric(k.replace('_', ' ').title(), v)
                        else:
                            st.write("**" + k.replace('_', ' ').title() + ":** " + str(v))
            else:
                st.markdown("- " + str(item))

def render_dict_data(key, value):
    st.markdown("### " + key.replace('_', ' ').title())
    
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
                    st.markdown("**" + k.replace('_', ' ').title() + ":** " + str(v))

def render_service_data(service_name, data):
    st.markdown("## " + service_name.replace('_', ' ').title())
    
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
            st.write("**" + key.replace('_', ' ').title() + ":** " + str(value))
    
    st.markdown("---")

{services}
"""
