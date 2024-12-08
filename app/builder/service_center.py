import streamlit as st
import time
import os
from app.utils.service_manager import ServiceManager

def get_available_versions(service_name: str) -> list:
    """Get available versions of a service"""
    versions = []
    if os.path.exists(f"app/microservices/{service_name}/service.py"):
        versions.append("original")
    if os.path.exists(f"app/generated_services/{service_name}/service.py"):
        versions.append("generated")
    return versions

def render_service_manager():
    """Render the service manager interface"""
    st.title("Service Command Center")
    
    # Initialize the service manager in session state if it doesn't exist
    if 'service_manager' not in st.session_state:
        st.session_state.service_manager = ServiceManager()
    
    # Initialize service versions in session state
    if 'service_versions' not in st.session_state:
        st.session_state.service_versions = {}
    
    manager = st.session_state.service_manager
    services_status = manager.get_all_services_status()

    # Add Start/Stop All Services buttons at the top in a row
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Start All Services", help="Start all services", use_container_width=True):
            with st.spinner("Starting all services..."):
                for service_name in services_status.keys():
                    if services_status[service_name]["status"] != "running":
                        version = st.session_state.service_versions.get(service_name, "original")
                        result = manager.start_service(service_name, version)
                        if result["success"]:
                            st.success(f"Started {service_name}")
                        else:
                            st.error(f"Failed to start {service_name}: {result['message']}")
                time.sleep(1)
                st.rerun()
    
    with col2:
        if st.button("🛑 Stop All Services", help="Stop all running services", use_container_width=True):
            with st.spinner("Stopping all services..."):
                for service_name in services_status.keys():
                    if services_status[service_name]["status"] == "running":
                        result = manager.stop_service(service_name)
                        if result["success"]:
                            st.success(f"Stopped {service_name}")
                        else:
                            st.error(f"Failed to stop {service_name}: {result['message']}")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    st.markdown("### Services")
    
    # Create three columns for service groups
    cols = st.columns(3)
    
    for idx, (service_name, status) in enumerate(services_status.items()):
        with cols[idx % 3]:
            render_service_card(service_name, status, manager)

def render_service_card(service_name: str, status: dict, manager: ServiceManager):
    """Render a service control card"""
    with st.container():
        st.markdown(f"#### {service_name.replace('_', ' ').title()}")
        
        # Get available versions
        versions = get_available_versions(service_name)
        
        # Version selector
        if len(versions) > 1:
            version = st.radio(
                "Version:",
                versions,
                key=f"version_{service_name}",
                horizontal=True,
                help="Choose which version of the service to run"
            )
            st.session_state.service_versions[service_name] = version
        elif versions:
            version = versions[0]
            st.session_state.service_versions[service_name] = version
            st.caption(f"Using {version} version")
        else:
            st.error("No implementation found")
            return
        
        # Status and controls in the same line
        status_col, control_col = st.columns([3, 2])
        
        with status_col:
            if status["status"] == "running":
                st.markdown("🟢 Running")
            else:
                st.markdown("🔴 Stopped")
        
        with control_col:
            if status["status"] == "running":
                if st.button("Stop", key=f"stop_{service_name}"):
                    with st.spinner(f"Stopping {service_name}..."):
                        result = manager.stop_service(service_name)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                        time.sleep(1)
                        st.rerun()
            else:
                if st.button("Start", key=f"start_{service_name}"):
                    version = st.session_state.service_versions.get(service_name, "original")
                    with st.spinner(f"Starting {service_name} ({version} version)..."):
                        result = manager.start_service(service_name, version)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                        time.sleep(1)
                        st.rerun()

        # Show recent logs if expanded
        if st.checkbox("Show Logs", key=f"logs_{service_name}"):
            logs = manager.get_service_logs(service_name)
            if logs:
                st.code("".join(logs[-10:]), language="text")
            else:
                st.info("No logs available")

if __name__ == "__main__":
    render_service_manager()