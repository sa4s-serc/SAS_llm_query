import os
import streamlit as st
from app.utils.app_generator import AppGenerator
import app.config as config
from app.utils.logger import setup_logger
from app.utils.chatbot import take_input


class BuilderApp:
    def __init__(self):
        self.logger = setup_logger("BuilderApp")
        if config.MICROSERVICES_DIR is None:
            self.logger.error(
                "MICROSERVICES_DIR is None. Make sure config.set_paths() and config.setup() have been called."
            )
            raise ValueError(
                "MICROSERVICES_DIR is not set. Configuration may not have been initialized properly."
            )
        self.all_services = self._discover_services(config.MICROSERVICES_DIR)
        self.app_generator = AppGenerator()
        # print("builder instance created")

    def _discover_services(self, directory):
        services = []
        if not os.path.exists(directory):
            self.logger.error(f"Directory does not exist: {directory}")
            return services
        for root, dirs, files in os.walk(directory):
            for dir in dirs:
                if dir.startswith("__"):
                    continue
                services.append(dir)

        return services

    def run(self):
        st.title(f"{config.APP_NAME} Builder")

        st.write(
            "Select the features you want in your personalized IIIT Companion app:"
        )

        selected_keywords = st.multiselect("Select features:", self.all_services)
        self.logger.info("Starting BuilderApp")
        if "conversation" not in st.session_state:
            st.session_state.conversation = []

        user_input = st.text_input(
            "Enter a sentence describing your desired app features:"
        )
        if user_input:
            selected_keywords = take_input(user_input)
            while selected_keywords is None:
                st.session_state.conversation.append(selected_keywords)
                selected_keywords = take_input(selected_keywords)
            self.logger.info(f"Selected Keywords: {selected_keywords}")
            st.write(f"Selected Keywords: {selected_keywords}")

        if st.button("Create My IIIT Companion App"):
            if selected_keywords:
                app_url = self.app_generator.generate_app(selected_keywords)
                st.success(
                    f"Your personalized {config.APP_NAME} app has been created! Access it at: {app_url}"
                )
            else:
                st.error("No valid features selected. Please try again.")

        return selected_keywords


if __name__ == "__main__":
    app = BuilderApp()
    app.run()
