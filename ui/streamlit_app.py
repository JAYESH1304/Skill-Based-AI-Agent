"""
Streamlit interface for the Skill-Based Agent
(with dataset upload support)
"""

import streamlit as st
import sys
from pathlib import Path
import pandas as pd
import tempfile

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from core.agent import SkillBasedAgent
from utils.logger import logger
from config import Config


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Skill-Based Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
        .stTextInput > div > div > input {
            font-size: 16px;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
            display: flex;
            flex-direction: column;
        }
        .chat-message.user {
            background-color: #e3f2fd;
        }
        .chat-message.assistant {
            background-color: #f5f5f5;
        }
        .chat-message .role {
            font-weight: bold;
            margin-bottom: 0.5rem;
        }
        .skill-badge {
            display: inline-block;
            padding: 0.2rem 0.5rem;
            background-color: #4CAF50;
            color: white;
            border-radius: 0.3rem;
            font-size: 0.8rem;
            margin: 0.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# Initialize session state
# -----------------------------
if "agent" not in st.session_state:
    try:
        st.session_state.agent = SkillBasedAgent()
        st.session_state.messages = []
        st.session_state.skills_loaded = True
        st.session_state.dataset = None
        st.session_state.dataset_path = None
    except Exception as e:
        st.error(f"Failed to initialize agent: {str(e)}")
        st.info("Please check your .env file and ensure all required variables are set.")
        st.session_state.skills_loaded = False


# -----------------------------
# Helper functions
# -----------------------------
def display_message(role: str, content: str, skills: list = None):
    """Display a chat message."""
    css_class = "user" if role == "user" else "assistant"
    role_emoji = "👤" if role == "user" else "🤖"

    with st.container():
        st.markdown(
            f"""
            <div class="chat-message {css_class}">
                <div class="role">{role_emoji} {role.capitalize()}</div>
                <div>{content}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if skills and role == "assistant":
            st.markdown("**Active Skills:**")
            cols = st.columns(len(skills))
            for i, skill in enumerate(skills):
                with cols[i]:
                    st.markdown(
                        f'<span class="skill-badge">{skill.name}</span>',
                        unsafe_allow_html=True,
                    )


# -----------------------------
# Main app
# -----------------------------
def main():
    # =========================
    # Sidebar
    # =========================
    with st.sidebar:
        st.title("⚙️ Agent Settings")

        if not st.session_state.skills_loaded:
            st.error("Agent not initialized properly")
            return

        # ---------------------
        # Skills
        # ---------------------
        st.subheader("📚 Available Skills")
        with st.expander("View All Skills"):
            skills_summary = st.session_state.agent.get_available_skills()
            st.markdown(skills_summary)

        # ---------------------
        # Options
        # ---------------------
        st.subheader("🎛️ Options")
        use_skills = st.checkbox(
            "Use Skills", value=True, help="Enable automatic skill matching"
        )
        stream_response = st.checkbox(
            "Stream Response", value=True, help="Stream responses in real-time"
        )

        # ---------------------
        # Dataset Upload
        # ---------------------
        st.subheader("📂 Upload Dataset")

        uploaded_file = st.file_uploader(
            "Upload CSV or Excel file", type=["csv", "xlsx"]
        )

        if uploaded_file is not None:
            try:
                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=uploaded_file.name
                ) as tmp:
                    tmp.write(uploaded_file.getbuffer())
                    st.session_state.dataset_path = tmp.name

                if uploaded_file.name.endswith(".csv"):
                    st.session_state.dataset = pd.read_csv(uploaded_file)
                else:
                    st.session_state.dataset = pd.read_excel(uploaded_file)

                st.success("Dataset uploaded successfully!")

                with st.expander("🔍 Preview Dataset"):
                    st.dataframe(st.session_state.dataset.head())

            except Exception as e:
                st.error(f"Failed to load dataset: {e}")

        # ---------------------
        # Actions
        # ---------------------
        st.subheader("🔧 Actions")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("🔄 Reload Skills"):
                with st.spinner("Reloading skills..."):
                    st.session_state.agent.reload_skills()
                    st.success("Skills reloaded!")

        with col2:
            if st.button("🗑️ Clear Chat"):
                st.session_state.agent.clear_history()
                st.session_state.messages = []
                st.session_state.dataset = None
                st.session_state.dataset_path = None
                st.success("Chat & dataset cleared!")
                st.rerun()

        # ---------------------
        # Config info
        # ---------------------
        st.subheader("ℹ️ Configuration")
        with st.expander("View Config"):
            st.code(
                f"""
Endpoint: {Config.AZURE_OPENAI_ENDPOINT}
Deployment: {Config.AZURE_OPENAI_DEPLOYMENT_NAME}
Max Tokens: {Config.MAX_TOKENS}
Temperature: {Config.TEMPERATURE}
Skills Directory: {Config.SKILLS_DIRECTORY}
"""
            )

    # =========================
    # Main Chat Interface
    # =========================
    st.title("🤖 Skill-Based AI Agent")
    st.markdown("Ask me anything! I'll use my specialized skills to help you.")

    # Display chat history
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("skills"),
        )

    # Chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        # Inject dataset context if available
        if st.session_state.dataset is not None:
            user_input = (
                f"A dataset has been uploaded with columns: "
                f"{list(st.session_state.dataset.columns)}.\n\n"
                f"User query: {user_input}"
            )

        # Store & display user message
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        display_message("user", user_input)

        # Agent response
        with st.spinner("🤔 Thinking..."):
            try:
                if stream_response:
                    response_placeholder = st.empty()
                    full_response = ""

                    for chunk in st.session_state.agent.process_query(
                        user_input, use_skills=use_skills, stream=True
                    ):
                        full_response += chunk
                        with response_placeholder.container():
                            display_message(
                                "assistant",
                                full_response,
                                st.session_state.agent.current_skills
                                if use_skills
                                else None,
                            )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": full_response,
                            "skills": st.session_state.agent.current_skills
                            if use_skills
                            else None,
                        }
                    )

                else:
                    response = st.session_state.agent.process_query(
                        user_input, use_skills=use_skills, stream=False
                    )

                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": response,
                            "skills": st.session_state.agent.current_skills
                            if use_skills
                            else None,
                        }
                    )

                    display_message(
                        "assistant",
                        response,
                        st.session_state.agent.current_skills
                        if use_skills
                        else None,
                    )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                logger.error(f"Error in Streamlit app: {str(e)}")

    # ---------------------
    # Footer
    # ---------------------
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "Powered by Azure OpenAI | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
