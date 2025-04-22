import streamlit as st
from api_helpers import handle_login, handle_signup, handle_user_question
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
    st.write("### Login")
    with st.form("login_form"):
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        submitted = st.form_submit_button("Login")
        if submitted:
            success, message = handle_login(login_username, login_password)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    st.write("### Signup")
    with st.form("signup_form"):
        signup_username = st.text_input("New Username", key="signup_username")
        signup_email = st.text_input("Email", key="signup_email")
        signup_password = st.text_input("Password", type="password", key="signup_password")
        signup_submitted = st.form_submit_button("Signup")
        
        if signup_submitted:
            success, message = handle_signup(signup_username, signup_email, signup_password)
            if success:
                st.success(message)
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
    
    # Display chat history
    for message in st.session_state.chat_history:
        # Display user message with user avatar
        with st.chat_message("user"):
            st.write(message["user"])
        
        # Display assistant message with assistant avatar
        with st.chat_message("assistant"):
            st.write(message["assistant"])

    user_question = st.chat_input("Ask your legal question here...", key="chat_input")
    
    # Handle the chat input when the user submits a question
    if user_question:
        success, error = handle_user_question(user_question)
        if not success and error:
            st.error(error)