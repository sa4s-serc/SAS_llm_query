import os
import streamlit as st
from app.utils.app_generator import AppGenerator
import app.config as config
from app.utils.logger import setup_logger
from app.utils.chatbot import chatbot_conversation, initialize_conversation


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

        if "conversation_state" not in st.session_state:
            st.session_state.conversation_state = initialize_conversation()

        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        for message in st.session_state.conversation_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Type your message here...")

        if user_input:
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            with st.chat_message("assistant"):
                response, st.session_state.conversation_state = chatbot_conversation(user_input, st.session_state.conversation_state)
                st.write(response)
            st.session_state.conversation_history.append({"role": "assistant", "content": response})

        if st.session_state.conversation_state["pass"] == 4:
            if st.button("Create My IIIT Companion App"):
                app_url = self.app_generator.generate_app(
                    st.session_state.conversation_state["suggested_services"],
                    st.session_state.conversation_state["parameters"]
                )
                st.success(f"Your personalized {config.APP_NAME} app has been created! Access it at: {app_url}")
                st.session_state.conversation_state = initialize_conversation()
                st.session_state.conversation_history = []


if __name__ == "__main__":
    app = BuilderApp()
    app.run()
