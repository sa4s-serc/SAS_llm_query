import streamlit as st
import os
from app.utils.service_manager import render_service_manager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_admin_access():
    """Check if admin features are enabled and user has correct password"""
    if not os.getenv("ENABLE_ADMIN_FEATURES", "false").lower() == "true":
        st.error("Admin features are disabled")
        return False
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.markdown("## 🔐 Admin Login")
        with st.form("admin_login"):
            password = st.text_input("Admin Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if password == os.getenv("ADMIN_PASSWORD"):
                    st.session_state.admin_authenticated = True
                    st.rerun()
                else:
                    st.error("Invalid password")
                    return False
        return False
    
    return True

def render_developer_options():
    """Render developer options section"""
    st.markdown("## 🛠️ Developer Options")
    
    # Debug Mode
    debug_enabled = os.getenv("ENABLE_DEBUG", "false").lower() == "true"
    if st.toggle("Enable Debug Mode", value=debug_enabled, key="debug_toggle"):
        st.info("Debug mode is enabled")
        # Add any debug-specific options here
        st.text_area("Debug Log Level", value="INFO", key="debug_log_level")
        st.number_input("Debug Port", value=9999, key="debug_port")
    
    # Environment Variables
    st.markdown("### Environment Variables")
    env_vars = {
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL", ""),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", ""),
        "MAX_EXCHANGES": os.getenv("MAX_EXCHANGES", ""),
        "BUILDER_PORT": os.getenv("BUILDER_PORT", ""),
        "SERVICE_MANAGER_PORT": os.getenv("SERVICE_MANAGER_PORT", "")
    }
    
    for key, value in env_vars.items():
        st.text_input(key, value=value, disabled=True)

def main():
    st.set_page_config(
        page_title="Admin Panel",
        page_icon="⚙️",
        layout="wide"
    )
    
    if not check_admin_access():
        if os.getenv("ENABLE_ADMIN_FEATURES", "false").lower() != "true":
            st.error("This page is not accessible. Please contact your administrator.")
        return
    
    st.title("⚙️ Admin Control Panel")
    
    # Create tabs for different admin sections
    tab1, tab2 = st.tabs(["🔧 Service Manager", "🛠️ Developer Options"])
    
    with tab1:
        render_service_manager()
    
    with tab2:
        render_developer_options()
    
    # Add logout button
    if st.sidebar.button("Logout"):
        st.session_state.admin_authenticated = False
        st.rerun()

if __name__ == "__main__":
    main() 