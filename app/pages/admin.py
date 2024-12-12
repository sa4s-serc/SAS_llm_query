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
                
                # Common locations for location-based services
                locations = ['Lumbini Park', 'HITEC City', 'Charminar', 'Hussain Sagar', 'KBR National Park', 
                           'Durgam Cheruvu Lake', 'Golconda Fort', 'Mecca Masjid']
                
                if service in ['air_quality', 'water_quality', 'crowd_monitor']:
                    parameters[service] = {
                        'location': st.multiselect(
                            f"Select locations for {service}:", 
                            options=locations,
                            key=f"{service}_loc"
                        ),
                        'timestamp': st.text_input(
                            "Timestamp (optional, format: YYYY-MM-DDTHH:MM:SS)", 
                            key=f"{service}_time"
                        )
                    }
                
                elif service == 'restaurant_finder':
                    parameters[service] = {
                        'cuisine_type': st.multiselect(
                            "Select cuisine types:", 
                            ['Indian', 'Chinese', 'Italian', 'Mexican', 'Continental', 'Thai', 'Fast Food', 'Vegetarian', 'Vegan'],
                            key=f"{service}_cuisine"
                        ),
                        'price_range': st.multiselect(
                            "Select price range (₹):",
                            [500, 750, 1000, 1300, 2500],
                            key=f"{service}_price"
                        ),
                        'dietary_restrictions': st.multiselect(
                            "Select dietary restrictions:",
                            ['None', 'Vegetarian', 'Vegan', 'Gluten-Free', 'Nut-Free'],
                            key=f"{service}_diet"
                        ),
                        'group_size': st.number_input(
                            "Group size:",
                            min_value=1,
                            max_value=20,
                            value=2,
                            key=f"{service}_group"
                        )
                    }
                
                elif service == 'travel_options':
                    parameters[service] = {
                        'destination': st.multiselect(
                            "Select destinations:",
                            locations,
                            key=f"{service}_dest"
                        ),
                        'preferred_mode': st.multiselect(
                            "Select preferred travel modes:",
                            ['walk', 'public_transport', 'private_transport'],
                            key=f"{service}_mode"
                        ),
                        'available_time': st.number_input(
                            "Available time (in hours):",
                            min_value=1,
                            max_value=12,
                            value=2,
                            key=f"{service}_time"
                        )
                    }
                
                elif service == 'historical_info':
                    parameters[service] = {
                        'site_name': st.multiselect(
                            "Select historical sites:",
                            ['Charminar', 'Golconda Fort', 'Mecca Masjid', 'Chowmahalla Palace', 
                             'Qutb Shahi Tombs', 'Salar Jung Museum'],
                            key=f"{service}_sites"
                        )
                    }
                
                elif service == 'exhibition_tracker':
                    parameters[service] = {
                        'interested_audience': st.multiselect(
                            "Select interested audience types:",
                            ['Art Lovers', 'Fashion Enthusiasts', 'Foodies', 'Collectors', 'Tech Buffs'],
                            key=f"{service}_audience"
                        ),
                        'exhibition_type': st.multiselect(
                            "Select exhibition types:",
                            ['Home Decor Exhibition', 'Fashion Show', 'Cosmetics Expo', 'Music Festival',
                             'Textile Fair', 'Craft Beer Festival', 'Wellness Expo', 'Antique Fair',
                             'Handicrafts Fair', 'Shoe Exhibition', 'Gardening Show'],
                            key=f"{service}_type"
                        )
                    }
                
                elif service == 'event_notifier':
                    parameters[service] = {
                        'event_type': st.multiselect(
                            "Select event types:",
                            ['Cultural', 'Sports', 'Music', 'Food', 'Art', 'Technology', 'Business'],
                            key=f"{service}_type"
                        ),
                        'duration': st.multiselect(
                            "Select event durations:",
                            ['1 Day', '2-3 Days', 'Week Long', 'Month Long'],
                            key=f"{service}_duration"
                        )
                    }
                
                elif service == 'ticket_purchase':
                    parameters[service] = {
                        'event_name': st.multiselect(
                            "Select events:",
                            ['Cultural Festival', 'Music Concert', 'Art Exhibition', 'Food Festival',
                             'Tech Conference', 'Sports Event', 'Theater Show'],
                            key=f"{service}_events"
                        ),
                        'price_range': st.slider(
                            "Price range (₹):",
                            min_value=0,
                            max_value=5000,
                            value=(500, 2000),
                            key=f"{service}_price"
                        )
                    }

    # Generate button
    if selected_services:
        if st.button("Generate Test App"):
            try:
                # Clean up parameters
                for service in parameters:
                    parameters[service] = {k: v for k, v in parameters[service].items() if v}
                
                # Pass empty conversation history for manual generation
                app_url = app_generator.generate_app(
                    selected_services,
                    parameters,
                    conversation_history=[]
                )
                st.success(f"Test app generated successfully! Access it at: {app_url}")
            except Exception as e:
                st.error(f"Error generating app: {str(e)}")
                st.error("Check logs for more details")

def render_feedback_analysis():
    """Render the feedback analysis section"""
    st.header("Feedback Analysis")
    
    # Initialize feedback collector with correct path
    feedback_collector = FeedbackCollector(feedback_dir="app/data")
    stats = feedback_collector.get_feedback_stats()
    
    # Display statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Responses", stats.get("total_responses", 0))
    with col2:
        st.metric("Average App Rating", f"{stats.get('average_app_rating', 0):.2f}/5")
    with col3:
        st.metric("Average Accuracy", f"{stats.get('average_accuracy', 0):.2f}/5")
    with col4:
        st.metric("Would Use Again", f"{stats.get('would_use_again_percentage', 0):.1f}%")

    # Display raw feedback data
    if st.checkbox("Show Raw Feedback Data"):
        try:
            import pandas as pd
            df = pd.read_csv("app/data/user_feedback.csv")
            st.dataframe(df)
        except Exception as e:
            st.error(f"Error reading feedback data: {str(e)}")
    
    # Display common services feedback
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Most Commonly Missing Services")
        missing_services = stats.get("most_common_missing_services", [])
        if missing_services:
            for service in missing_services:
                st.write(f"- {service}")
        else:
            st.info("No data available")
    
    with col2:
        st.subheader("Most Commonly Unnecessary Services")
        unnecessary_services = stats.get("most_common_unnecessary_services", [])
        if unnecessary_services:
            for service in unnecessary_services:
                st.write(f"- {service}")
        else:
            st.info("No data available")
    
    # Display feedback summary
    st.subheader("Feedback Summary")
    summary_cols = st.columns(2)
    
    with summary_cols[0]:
        st.markdown("#### Rating Distribution")
        try:
            df = pd.read_csv("app/data/user_feedback.csv")
            for rating_type in ['app_rating', 'accuracy_rating', 'relevance_rating']:
                if rating_type in df.columns:
                    avg_rating = df[rating_type].mean()
                    st.write(f"{rating_type.replace('_', ' ').title()}: {avg_rating:.2f}/5")
        except Exception as e:
            st.error(f"Error calculating rating distribution: {str(e)}")
    
    with summary_cols[1]:
        st.markdown("#### Recent Feedback")
        try:
            df = pd.read_csv("app/data/user_feedback.csv")
            recent_feedback = df.sort_values('timestamp', ascending=False).head(5)
            for _, row in recent_feedback.iterrows():
                with st.expander(f"Feedback from {row.get('user_name', 'Anonymous')} - {row['timestamp']}"):
                    st.write(f"Overall Experience: {row.get('overall_experience', 'N/A')}")
                    st.write(f"App Rating: {row.get('app_rating', 'N/A')}/5")
                    if row.get('other_suggestions'):
                        st.write(f"Suggestions: {row['other_suggestions']}")
        except Exception as e:
            st.error(f"Error displaying recent feedback: {str(e)}")

def render_debug_info():
    """Render debug information section"""
    st.header("Debug Information")
    
    if st.checkbox("Show Environment Variables"):
        st.json({k: v for k, v in os.environ.items() if not k.startswith(('_', 'PATH'))})
    
    if st.checkbox("Show Service Port Mappings"):
        port_manager = get_port_manager()
        services = port_manager.get_all_services()
        
        # Create a more readable port mapping display
        port_mappings = {}
        for service_name, info in services.items():
            port_mappings[service_name] = {
                "port": info.get("port", "N/A"),
                "status": "Running" if info.get("enabled", False) else "Stopped",
                "pid": info.get("pid", "N/A"),
                "last_updated": info.get("last_updated", "Never")
            }
        st.json(port_mappings)
    
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