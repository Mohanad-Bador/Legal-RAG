import streamlit as st
from api_helpers import handle_login, handle_signup, toggle_signup_modal, handle_user_question, render_chat_history, render_about_modal
from sidebar import render_sidebar
from style_utils import load_css
from session_manager import initialize_session_state, load_persistent_session

# Page configuration
st.set_page_config(
    page_title="Legal RAG",
    page_icon="⚖️",
    initial_sidebar_state="expanded"
)

# Load CSS and initialize session
load_css()
initialize_session_state()
load_persistent_session()

# Streamlit app UI
col1, col2 = st.columns([4, 1])
with col1:
    st.title("Egyptian Legal Assistant")
with col2:
    # Add some padding to align with the title
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("ℹ️ About", key="about_btn", type="primary"):
        render_about_modal()

# Login and Signup forms
if not st.session_state.logged_in:
    # Initialize modal state if not exists
    if 'show_signup_modal' not in st.session_state:
        st.session_state.show_signup_modal = False
    
    st.write("### Login")
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        login_password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        # Modified columns with signup text
        col1, col2 = st.columns([1, 2])
        with col1:
            submitted = st.form_submit_button("Login")
        with col2:
            # Create a subcolumns layout for the signup button and text
            subcol1, subcol2 = st.columns([3, 2])
            with subcol1:
                st.markdown("<div style='padding-top: 5px;'>Sign up if you don't have an account</div>", unsafe_allow_html=True)
            with subcol2:
                signup_button = st.form_submit_button("Signup", on_click=toggle_signup_modal)
        
        if submitted:
            success, message = handle_login(login_username, login_password)
            if success:
                if st.session_state.show_signup_modal:
                    toggle_signup_modal()  # Close signup modal if open
                st.success(message)
                st.rerun()
            else:
                st.error(message)
    
    # Display signup form in a card-like container when show_signup_modal is True
    if st.session_state.show_signup_modal:
        # Create a container for the modal-like appearance
        modal_container = st.container()
        with modal_container:
            # Add some styling to make it look like a modal
            st.markdown("""
                <div class="signup-modal">
                <h3>Create a New Account</h3>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("signup_modal_form"):
                signup_username = st.text_input("New Username", key="signup_username", placeholder="Enter your username (e.g., john_doe)")
                signup_email = st.text_input("Email", key="signup_email", placeholder="Enter your email (e.g., john@gmail.com)")
                signup_password = st.text_input("Password", type="password", key="signup_password", placeholder="Min 8 chars, letters & digits required")
                signup_cols = st.columns([1, 1])
                with signup_cols[0]:
                    signup_submitted = st.form_submit_button("Create Account")
                with signup_cols[1]:
                    cancel_button = st.form_submit_button("Cancel", on_click=toggle_signup_modal)
                
                if signup_submitted:
                    success, message = handle_signup(signup_username, signup_email, signup_password)
                    if success:
                        st.success(message)
                        st.session_state.show_signup_modal = False
                        st.rerun()
                    else:
                        st.error(message)
else:
    # Render sidebar with chat list
    render_sidebar()

    # Main chat area
    if st.session_state.current_chat_id is None:
        st.write("### How Can I Help You?")
    
    # Display current chat title if a chat is selected
    if st.session_state.current_chat_id:
        current_chat = next((chat for chat in st.session_state.chat_list if chat["id"] == st.session_state.current_chat_id), None)
        if current_chat:
            st.write(f"### Current Chat: {current_chat['title']}")

    # Display chat history with context expanders
    render_chat_history()

    user_question = st.chat_input("Ask your legal question here...", key="chat_input")
    
    # Handle the chat input when the user submits a question
    if user_question:
        success, error = handle_user_question(user_question)
        if not success and error:
            st.error(error)