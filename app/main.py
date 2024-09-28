import os
import sys
import streamlit as st
from app.builder.builder_app import BuilderApp
import app.config as config
from app.utils.logger import setup_logger

logger = setup_logger("main")


def setup_configuration():
    # Get the absolute path of the current file
    current_file = os.path.abspath(__file__)

    # Get the app directory (same level as the current file)
    app_dir = os.path.dirname(current_file)

    # Set up the configuration
    logger.info(f"Setting up configuration with app_dir: {app_dir}")
    config.set_paths(app_dir)
    config.setup()

    logger.info(f"MICROSERVICES_DIR: {config.MICROSERVICES_DIR}")
    logger.info(f"GENERATED_APPS_DIR: {config.GENERATED_APPS_DIR}")


# streamlit is creating a new instance of builder app every time, to prevent that, we need to store the instance in session state
def get_builder_app():
    if "builder_app" not in st.session_state:
        setup_configuration()
        st.session_state.builder_app = BuilderApp()
    return st.session_state.builder_app


def run_builder_app():
    try:
        st.set_page_config(
            page_title="IIIT Companion Builder", page_icon="🏗️", layout="wide"
        )
        builder_app = get_builder_app()
        builder_app.run()
    except Exception as e:
        logger.error(f"Error setting up the application: {str(e)}", exc_info=True)
        st.error(f"An error occurred while setting up the application: {str(e)}")


if __name__ == "__main__":
    run_builder_app()
