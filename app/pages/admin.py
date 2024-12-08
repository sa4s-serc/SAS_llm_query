import streamlit as st
import os
from app.builder.service_center import render_service_manager
from app.utils.logger import setup_logger

logger = setup_logger("AdminPage")

def check_admin_password():
    """Check if admin password is correct"""
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        admin_password = os.getenv("ADMIN_PASSWORD", "123")
        password = st.text_input("Enter admin password:", type="password")
        
        if st.button("Login"):
            if password == admin_password:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password!")
        return False
    return True

def main():
    st.title("Admin Panel")
    
    if not check_admin_password():
        return

    # Show service manager
    render_service_manager()

if __name__ == "__main__":
    main() 