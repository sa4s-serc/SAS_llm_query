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


def run_builder_app():
    try:
        setup_configuration()

        st.set_page_config(
            page_title="IIIT Companion Builder", page_icon="🏗️", layout="wide"
        )
        builder_app = BuilderApp()
        builder_app.run()
    except Exception as e:
        logger.error(f"Error setting up the application: {str(e)}", exc_info=True)
        st.error(f"An error occurred while setting up the application: {str(e)}")


if __name__ == "__main__":
    run_builder_app()
