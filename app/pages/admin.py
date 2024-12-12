import streamlit as st
import os
from app.builder.service_center import render_service_manager
from app.utils.logger import setup_logger
from app.utils.om2m_utils import OM2MManager
from app.utils.service_manager import ServiceManager
from app.utils.feedback_collector import FeedbackCollector
from app.utils.app_generator import AppGenerator
from app.utils.port_manager import get_port_manager

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

def render_manual_app_generator():
    """Render the manual app generator section"""
    st.header("Manual App Generator")
    
    service_manager = ServiceManager()
    app_generator = AppGenerator()
    
    # Service selection
    st.subheader("Select Services")
    available_services = service_manager.get_available_services()
    selected_services = st.multiselect(
        "Choose services to include in the app:",
        options=available_services,
        default=[],
        help="Select one or more services to include in your generated app"
    )

    # Parameters configuration
    st.subheader("Configure Parameters")
    parameters = {}
    if selected_services:
        for service in selected_services:
            st.markdown(f"**{service} Parameters**")
            service_info = service_manager.get_service_info(service)
            if service_info:
                st.markdown(f"*{service_info.get('description', 'No description available')}*")
                # Add default parameters based on service type
                if service in ['air_quality', 'water_quality', 'crowd_monitor']:
                    parameters[service] = {
                        'location': st.multiselect(f"Select locations for {service}:", 
                                                 ['Lumbini Park', 'HITEC City', 'Charminar', 'Hussain Sagar'],
                                                 key=f"{service}_loc")
                    }
                elif service == 'restaurant_finder':
                    parameters[service] = {
                        'cuisine_type': st.multiselect("Select cuisine types:", 
                                                     ['Indian', 'Chinese', 'Italian', 'Continental'],
                                                     key=f"{service}_cuisine"),
                        'price_range': st.slider("Price range (₹)", 0, 5000, (500, 2000), key=f"{service}_price")
                    }
                elif service == 'travel_options':
                    parameters[service] = {
                        'preferred_mode': st.multiselect("Select travel modes:",
                                                       ['walk', 'public_transport', 'private_transport'],
                                                       key=f"{service}_mode")
                    }

    # Generate button
    if selected_services:
        if st.button("Generate Test App"):
            try:
                app_url = app_generator.generate_app(selected_services, parameters)
                st.success(f"Test app generated successfully! Access it at: {app_url}")
            except Exception as e:
                st.error(f"Error generating app: {str(e)}")

def render_feedback_analysis():
    """Render the feedback analysis section"""
    st.header("Feedback Analysis")
    
    feedback_collector = FeedbackCollector()
    stats = feedback_collector.get_feedback_stats()
    
    # Display statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Responses", stats.get("total_responses", 0))
    with col2:
        st.metric("Average Accuracy", f"{stats.get('average_accuracy', 0):.2f}/5")
    with col3:
        st.metric("Would Use Again", f"{stats.get('would_use_again_percentage', 0):.1f}%")

    # Display common services feedback
    st.subheader("Most Commonly Missing Services")
    st.write(stats.get("most_common_missing_services", []))
    
    st.subheader("Most Commonly Unnecessary Services")
    st.write(stats.get("most_common_unnecessary_services", []))

def render_debug_info():
    """Render debug information section"""
    st.header("Debug Information")
    
    if st.checkbox("Show Environment Variables"):
        st.json({k: v for k, v in os.environ.items() if not k.startswith(('_', 'PATH'))})
    
    if st.checkbox("Show Port Mappings"):
        port_manager = get_port_manager()
        st.json(port_manager.get_all_ports())
    
    if st.checkbox("Show Service Configurations"):
        service_manager = ServiceManager()
        st.json(service_manager.services_config)

def main():
    st.title("Admin Panel")
    
    if not check_admin_password():
        return

    # Create tabs for different admin sections
    tabs = st.tabs([
        "Service Manager",
        "OM2M Manager",
        "Manual App Generator",
        "Feedback Analysis",
        "Debug Info"
    ])
    
    with tabs[0]:
        render_service_manager()
    
    with tabs[1]:
        render_om2m_manager()
        
    with tabs[2]:
        render_manual_app_generator()
        
    with tabs[3]:
        render_feedback_analysis()
        
    with tabs[4]:
        render_debug_info()

if __name__ == "__main__":
    main() 