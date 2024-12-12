import streamlit as st
import os
from utils.chatbot import initialize_conversation, chatbot_conversation
from utils.feedback_collector import FeedbackCollector
from utils.app_generator import AppGenerator
from utils.service_manager import ServiceManager

class BuilderApp:
    def __init__(self):
        self.initialize_components()

    def initialize_components(self):
        self.app_generator = AppGenerator()
        self.feedback_collector = FeedbackCollector()
        self.service_manager = ServiceManager()

    def show_welcome_message(self):
        st.title("Welcome to City Companion Builder! 🏛️")
        
        st.markdown("""
        <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 1.5rem;'>
            Imagine you're in Hyderabad with only a few hours to explore. You need different apps—one for metro routes, 
            another for restaurants, one for weather updates, booking tickets, and more. But what if there was one app 
            that could understand your schedule, preferences, and needs, combining all these functionalities into a 
            single solution?
        </p>
        
        <p style='font-size: 1.1em; line-height: 1.6; margin-bottom: 1.5rem;'>
            <strong>That's exactly what we've built for you.</strong> Try it out and see how well it works. 
            It may not look perfect yet, but we want you to focus on how accurately it helps you complete your tasks.
        </p>
        
        <p style='font-size: 1.1em; line-height: 1.6; color: #2e6c80;'>
            After testing, please fill out the feedback form to share your experience and suggestions.
        </p>
        """, unsafe_allow_html=True)

    def show_feedback_form(self, user_query: str, selected_services: list):
        """Display feedback form and collect user responses"""
        st.markdown("### Help Us Improve! 📝")
        st.write("Please share your experience with our service:")

        # User name (optional)
        user_name = st.text_input(
            "Your Name (Optional)",
            help="Optional: Your name will help us better understand our users",
            key="feedback_name"
        )

        # Query summary
        query_summary = st.text_area(
            "Briefly summarize about the queries you have asked",
            help="This helps us understand how users interact with our system",
            key="query_summary"
        )

        # Application rating
        app_rating = st.slider(
            "Rate the application on a scale of 1 to 5",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Poor, 5 = Excellent",
            key="app_rating"
        )

        # Accuracy rating
        accuracy = st.slider(
            "How accurate were the selected services for your needs?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Not accurate at all, 5 = Extremely accurate",
            key="accuracy_rating"
        )

        # Relevance rating
        relevance = st.slider(
            "How relevant were the selected services to your query?",
            min_value=1,
            max_value=5,
            value=3,
            help="1 = Not relevant at all, 5 = Extremely relevant",
            key="relevance_rating"
        )

        # Missing services
        missing = st.multiselect(
            "Were there any services you expected but weren't selected?",
            options=self.service_manager.get_available_services(),
            default=[],
            key="missing_services"
        )

        # Unnecessary services
        unnecessary = st.multiselect(
            "Were any of the selected services unnecessary?",
            options=selected_services,
            default=[],
            key="unnecessary_services"
        )

        # Overall experience
        overall_experience = st.text_area(
            "How is your overall experience?",
            help="Please share your thoughts about using the application",
            key="overall_experience"
        )

        # Other suggestions
        other_suggestions = st.text_area(
            "Other suggestions / feedback",
            help="Any additional ideas or comments to help us improve",
            key="other_suggestions"
        )

        # Would use again
        would_use_again = st.checkbox("Would you use this system again?", value=True, key="would_use_again")

        # Submit button
        if st.button("Submit Feedback", key="submit_feedback"):
            feedback_data = {
                "user_name": user_name,
                "conversation_history": st.session_state.conversation_history,
                "query_summary": query_summary,
                "app_rating": app_rating,
                "selected_services": selected_services,
                "accuracy_rating": accuracy,
                "relevance_rating": relevance,
                "missing_services": missing,
                "unnecessary_services": unnecessary,
                "overall_experience": overall_experience,
                "other_suggestions": other_suggestions,
                "would_use_again": would_use_again
            }

            if self.feedback_collector.save_feedback(feedback_data):
                st.success("Thank you for your feedback! 🙏")
                return True
            else:
                st.error("Sorry, there was an error saving your feedback. Please try again.")
                return False

        return False

    def initialize_session_state(self):
        if 'conversation_state' not in st.session_state:
            st.session_state.conversation_state = initialize_conversation()
            st.session_state.generated_apps = []
            st.session_state.feedback_collector = FeedbackCollector()
            st.session_state.app_generator = AppGenerator()
            st.session_state.service_manager = ServiceManager()
            st.session_state.conversation_history = []
            st.session_state.feedback_submitted = False

    def run(self):
        # Show welcome message for first-time users
        if 'welcomed' not in st.session_state:
            self.show_welcome_message()
            if st.button("Get Started", key="welcome_button"):
                st.session_state.welcomed = True
                st.rerun()
            return

        # Main app content
        st.title("City Companion Builder")
        self.initialize_session_state()

        # Display conversation history
        for message in st.session_state.conversation_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        # Chat input
        user_input = st.chat_input("What kind of app would you like me to build for you?")

        if user_input:
            # Add user message to history
            st.session_state.conversation_history.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            # Get assistant response
            with st.chat_message("assistant"):
                response, st.session_state.conversation_state = chatbot_conversation(
                    user_input, 
                    st.session_state.conversation_state
                )
                st.write(response)
            st.session_state.conversation_history.append({"role": "assistant", "content": response})

        # Check if ready to create app
        if st.session_state.conversation_state.get("ready_for_app", False):
            selected_services = st.session_state.conversation_state.get("suggested_services", [])
            
            # Create two columns for app generation and feedback
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### Create Your App")
                st.write("Generate your personalized City Companion app with the selected services.")
                if st.button("Create City Companion App", key="create_app"):
                    app_url = self.app_generator.generate_app(
                        selected_services,
                        st.session_state.conversation_state.get("parameters", {})
                    )
                    st.success(f"Your personalized City Companion app has been created! Access it at: {app_url}")
                    
                # Show selected services
                st.markdown("### Selected Services")
                for service in selected_services:
                    st.markdown(f"- {service}")

            with col2:
                if not st.session_state.get("feedback_submitted", False):
                    feedback_submitted = self.show_feedback_form(
                        user_input or "No query provided",
                        selected_services
                    )
                    if feedback_submitted:
                        st.session_state.feedback_submitted = True
                        # Reset the conversation only after feedback is submitted
                        st.session_state.conversation_state = initialize_conversation()
                        st.session_state.conversation_history = []
                        st.rerun()
                else:
                    st.success("Thank you for your feedback! Start a new conversation to create another app.")
                    if st.button("Start New Conversation", key="new_conversation"):
                        st.session_state.conversation_state = initialize_conversation()
                        st.session_state.conversation_history = []
                        st.session_state.feedback_submitted = False
                        st.rerun()

def main():
    app = BuilderApp()
    app.run()

if __name__ == "__main__":
    main()
