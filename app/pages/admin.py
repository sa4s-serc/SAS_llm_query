import streamlit as st
import os
from app.builder.service_center import render_service_manager
from app.utils.logger import setup_logger
from app.utils.om2m_utils import OM2MManager

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

def render_om2m_manager():
    """Render the OM2M sensor management section"""
    st.header("OM2M Sensor Management")

    # Initialize OM2M Manager
    om2m_manager = OM2MManager()

    # Check CSE Status
    cse_status = om2m_manager.check_cse_exists()
    status_color = "green" if cse_status else "red"
    st.markdown(f"CSE Status: <span style='color: {status_color}'>{'✓ Connected' if cse_status else '✗ Not Connected'}</span>", unsafe_allow_html=True)

    if not cse_status:
        st.error("Cannot connect to OM2M server. Please ensure it's running.")
        return

    # Sensor Management Section
    st.subheader("Sensor Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Available Sensors")
        for sensor in om2m_manager.sensors:
            st.write(f"- {sensor}")

    with col2:
        st.markdown("### Actions")
        if st.button("Setup All Sensors"):
            with st.spinner("Setting up sensor structures..."):
                results = om2m_manager.setup_all_sensors()
                success_count = sum(1 for r in results if r["ae_created"])
                st.success(f"Successfully set up {success_count} out of {len(results)} sensors")

        if st.button("Check Sensor Status"):
            with st.spinner("Checking sensor status..."):
                status = {}
                for sensor in om2m_manager.sensors:
                    data = om2m_manager.get_sensor_data(sensor)
                    status[sensor] = "Active" if data else "Inactive"
                
                st.markdown("### Sensor Status")
                for sensor, state in status.items():
                    color = "green" if state == "Active" else "red"
                    st.markdown(f"- {sensor}: <span style='color: {color}'>{state}</span>", unsafe_allow_html=True)

    # Individual Sensor Management
    st.subheader("Individual Sensor Management")
    selected_sensor = st.selectbox("Select Sensor", om2m_manager.sensors)
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("Create Structure", key=f"create_{selected_sensor}"):
            with st.spinner(f"Creating structure for {selected_sensor}..."):
                result = om2m_manager.create_sensor_structure(selected_sensor)
                if result["ae_created"]:
                    st.success(f"Successfully created structure for {selected_sensor}")
                else:
                    st.error(f"Failed to create structure for {selected_sensor}")

    with col4:
        if st.button("Delete Structure", key=f"delete_{selected_sensor}"):
            if st.warning(f"Are you sure you want to delete {selected_sensor}?"):
                with st.spinner(f"Deleting structure for {selected_sensor}..."):
                    if om2m_manager.delete_sensor_structure(selected_sensor):
                        st.success(f"Successfully deleted structure for {selected_sensor}")
                    else:
                        st.error(f"Failed to delete structure for {selected_sensor}")

    # Sensor Data Viewer
    st.subheader("Sensor Data Viewer")
    view_sensor = st.selectbox("Select Sensor to View", om2m_manager.sensors, key="view_sensor")
    container_type = st.radio("Select Container", ["data", "metadata"])
    
    if st.button("View Latest Data", key=f"view_{view_sensor}"):
        with st.spinner(f"Fetching data for {view_sensor}..."):
            data = om2m_manager.get_sensor_data(view_sensor, container_type)
            if data:
                st.json(data)
            else:
                st.warning(f"No data available for {view_sensor}")

def main():
    st.title("Admin Panel")
    
    if not check_admin_password():
        return

    # Create tabs for different admin sections
    tab1, tab2 = st.tabs(["Service Manager", "OM2M Manager"])
    
    with tab1:
        render_service_manager()
    
    with tab2:
        render_om2m_manager()

if __name__ == "__main__":
    main() 