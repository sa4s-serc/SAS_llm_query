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
        self.keyword_tree = self._discover_services(config.MICROSERVICES_DIR)
        self.all_keywords = self.flatten_keywords(self.keyword_tree)
        self.app_generator = AppGenerator()

    def _discover_services(self, directory):
        tree = {}
        if not os.path.exists(directory):
            self.logger.error(f"Directory does not exist: {directory}")
            return tree
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path) and not item.startswith("__"):
                category = item
                tree[category] = []
                for service in os.listdir(item_path):
                    if service.endswith(".py") and not service.startswith("__"):
                        service_name = os.path.splitext(service)[0]
                        tree[category].append(service_name)
        return tree

    def flatten_keywords(self, tree):
        keywords = []
        for category, services in tree.items():
            keywords.append(category)
            keywords.extend(services)
        return keywords

    def run(self):
        st.title(f"{config.APP_NAME} Builder")

        st.write(
            "Select the features you want in your personalized IIIT Companion app:"
        )
        st.write("Selecting a category will include all its services.")

        selected_keywords = st.multiselect("Select features:", self.all_keywords)
        self.logger.info("Starting BuilderApp")
        if "conversation" not in st.session_state:
            st.session_state.conversation = []

        user_input = st.text_input(
            "Enter a sentence describing your desired app features:"
        )
        if user_input:
            selected_keywords = take_input(user_input)
            # print(selected_keywords)
            # Convert the string to a list of keywords
            while selected_keywords is None:
                st.session_state.conversation.append(selected_keywords)
                selected_keywords = take_input(selected_keywords)
            self.logger.info(f"Selected Keywords: {selected_keywords}")
            st.write(f"Selected Keywords: {selected_keywords}")

        if st.button("Create My IIIT Companion App"):
            if selected_keywords:
                processed_keywords = self.process_selected_keywords(selected_keywords)
                if processed_keywords:
                    app_url = self.app_generator.generate_app(processed_keywords)
                    st.success(
                        f"Your personalized {config.APP_NAME} app has been created! Access it at: {app_url}"
                    )
                else:
                    st.error("No valid features selected. Please try again.")
            else:
                st.error("Please enter a sentence to describe your desired features.")

    def process_selected_keywords(self, selected_keywords):
        processed_keywords = {}
        for keyword in selected_keywords:
            if keyword in self.keyword_tree:
                # If a category is selected, include all its services
                processed_keywords[keyword] = self.keyword_tree[keyword]
            else:
                # If a service is selected, find its category and add it
                for category, services in self.keyword_tree.items():
                    if keyword in services:
                        if category not in processed_keywords:
                            processed_keywords[category] = []
                        processed_keywords[category].append(keyword)

        self.logger.info(f"Processed keywords: {processed_keywords}")
        return processed_keywords


# Run the BuilderApp
if __name__ == "__main__":
    app = BuilderApp()
    app.run()
