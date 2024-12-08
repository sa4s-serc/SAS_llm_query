import os
import streamlit as st
from app.utils.app_generator import AppGenerator
import app.config as config
from app.utils.logger import setup_logger
from app.utils.chatbot import chatbot_conversation, initialize_conversation
from app.utils.feedback_collector import FeedbackCollector


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
        self.feedback_collector = FeedbackCollector()

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

    def show_feedback_form(self, user_query: str, selected_services: list):
        """Display feedback form and collect user responses"""
        st.markdown("### Help Us Improve! 📝")
        st.write("Please provide feedback about the selected services:")

        # Accuracy rating
        accuracy = st.slider(
            "How accurate were the selected services for your needs?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Not accurate at all, 5 = Extremely accurate"
        )

        # Relevance rating
        relevance = st.slider(
            "How relevant were the selected services to your query?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Not relevant at all, 5 = Extremely relevant"
        )

        # Missing services
        missing = st.multiselect(
            "Were there any services you expected but weren't selected?",
            options=self.all_services,
            default=[]
        )

        # Unnecessary services
        unnecessary = st.multiselect(
            "Were any of the selected services unnecessary?",
            options=selected_services,
            default=[]
        )

        # Additional comments
        comments = st.text_area(
            "Any additional comments or suggestions?",
            help="Optional: Please share any other thoughts about the service selection"
        )

        # Would use again
        would_use_again = st.checkbox("Would you use this system again?", value=True)

        # Submit button
        if st.button("Submit Feedback"):
            feedback_data = {
                "user_query": user_query,
                "selected_services": selected_services,
                "accuracy_rating": accuracy,
                "relevance_rating": relevance,
                "missing_services": missing,
                "unnecessary_services": unnecessary,
                "additional_comments": comments,
                "would_use_again": would_use_again
            }

            if self.feedback_collector.save_feedback(feedback_data):
                st.success("Thank you for your feedback! 🙏")
                return True
            else:
                st.error("Sorry, there was an error saving your feedback. Please try again.")
                return False

        return False

    def run(self):
        st.title(f"{config.APP_NAME} Builder")

        # Check if we're in admin mode (controlled by environment variable)
        dev_mode = os.getenv("ENABLE_DEBUG", "false").lower() == "true"

        if "conversation_state" not in st.session_state:
            st.session_state.conversation_state = initialize_conversation()

        if "conversation_history" not in st.session_state:
            st.session_state.conversation_history = []

        if "feedback_submitted" not in st.session_state:
            st.session_state.feedback_submitted = False

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

        # Check if ready to create app
        if st.session_state.conversation_state.get("ready_for_app", False):
            selected_services = st.session_state.conversation_state["suggested_services"]
            
            # Show feedback form if not submitted and not in dev mode
            if not st.session_state.feedback_submitted and not dev_mode:
                feedback_submitted = self.show_feedback_form(
                    user_input or "No query provided",
                    selected_services
                )
                if feedback_submitted:
                    st.session_state.feedback_submitted = True
            else:
                # In dev mode, automatically mark feedback as submitted
                st.session_state.feedback_submitted = True

            # Show create app button after feedback or in dev mode
            if st.session_state.feedback_submitted or dev_mode:
                if st.button(f"Create {config.APP_NAME} App"):
                    app_url = self.app_generator.generate_app(
                        selected_services,
                        st.session_state.conversation_state["parameters"]
                    )
                    st.success(f"Your personalized {config.APP_NAME} app has been created! Access it at: {app_url}")
                    st.session_state.conversation_state = initialize_conversation()
                    st.session_state.conversation_history = []
                    st.session_state.feedback_submitted = False


if __name__ == "__main__":
    app = BuilderApp()
    app.run()
