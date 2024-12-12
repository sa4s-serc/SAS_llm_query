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
            
            if st.button("Create City Companion App"):
                app_url = self.app_generator.generate_app(
                    selected_services,
                    st.session_state.conversation_state.get("parameters", {}),
                    st.session_state.conversation_history
                )
                st.success(f"Your personalized City Companion app has been created! Access it at: {app_url}")
                # Reset the conversation
                st.session_state.conversation_state = initialize_conversation()
                st.session_state.conversation_history = []

def main():
    app = BuilderApp()
    app.run()

if __name__ == "__main__":
    main()
