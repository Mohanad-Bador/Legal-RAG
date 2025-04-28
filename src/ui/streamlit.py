import streamlit as st
from api_helpers import handle_login, handle_signup, handle_user_question, render_chat_history
from sidebar import render_sidebar

# Initialize session state variables
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'access_token' not in st.session_state:
    st.session_state.access_token = ""
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'user_question' not in st.session_state:
    st.session_state.user_question = ""
if 'should_clear_input' not in st.session_state:
    st.session_state.should_clear_input = False
if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None
if 'chat_list' not in st.session_state:
    st.session_state.chat_list = []
if 'editing_chat_title' not in st.session_state:
    st.session_state.editing_chat_title = False

# Streamlit app UI
st.title("Egyptian Legal Assistant")

# Login and Signup forms
if not st.session_state.logged_in:
    # Initialize modal state if not exists
    if 'show_signup_modal' not in st.session_state:
        st.session_state.show_signup_modal = False
    
    # Function to toggle signup modal
    def toggle_signup_modal():
        st.session_state.show_signup_modal = not st.session_state.show_signup_modal
    
    st.write("### Login")
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
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
                <style>
                .signup-modal {
                    background-color: #ff4b4b;
                    padding: 20px;
                    border-radius: 10px;
                    border: 1px solid #ddd;
                    margin: 10px 0;
                }
                </style>
                <div class="signup-modal">
                <h3>Create a New Account</h3>
                </div>
            """, unsafe_allow_html=True)
            
            with st.form("signup_modal_form"):
                signup_username = st.text_input("New Username", key="signup_username")
                signup_email = st.text_input("Email", key="signup_email")
                signup_password = st.text_input("Password", type="password", key="signup_password")
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
    st.write("### Egyptian Legal Assistant")
    
    # Display current chat title if a chat is selected
    if st.session_state.current_chat_id:
        current_chat = next((chat for chat in st.session_state.chat_list if chat["id"] == st.session_state.current_chat_id), None)
        if current_chat:
            st.write(f"Current Chat: {current_chat['title']}")

    # Display chat history with context expanders
    render_chat_history()

    user_question = st.chat_input("Ask your legal question here...", key="chat_input")
    
    # Handle the chat input when the user submits a question
    if user_question:
        success, error = handle_user_question(user_question)
        if not success and error:
            st.error(error)