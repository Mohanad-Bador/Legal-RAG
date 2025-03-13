import streamlit as st
import requests
import time

# Custom CSS to style the chat messages
st.markdown(
    """
    <style>
    .user-message {
        text-align: right;
        background-color: #ff4b4b;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        textColor="#31333F";
    }
    .assistant-message {
        text-align: left;
        background-color: #262730;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
        textColor="#fafafa";
    }
    </style>
    """,
    unsafe_allow_html=True
)

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

# Streamlit app UI
st.title("Egyptian Legal Assistant")

# Login and Signup forms
if not st.session_state.logged_in:
    st.write("### Login")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        response = requests.post(
            "http://localhost:8000/auth/login",
            data={"username": login_username, "password": login_password}
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.logged_in = True
            st.session_state.username = login_username
            st.session_state.access_token = data["access_token"]
            st.session_state.user_id = data["user_id"]  # Now the response includes user_id
            st.success("Logged in successfully")
            time.sleep(2)  # Delay for 2 seconds
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.write("### Signup")
    signup_username = st.text_input("New Username", key="signup_username")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")

    if st.button("Signup"):
        response = requests.post(
            "http://localhost:8000/auth/signup",
            json={"username": signup_username, "email": signup_email, "password": signup_password}
        )
        if response.status_code == 200:
            data = response.json()
            st.success("User created successfully")
            st.session_state.logged_in = True
            st.session_state.username = signup_username
            st.session_state.user_id = data["user_id"]  # Now the response includes user_id
            time.sleep(2)  # Delay for 2 seconds
            st.rerun()
        else:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except ValueError:
                error_detail = response.text  # Fallback to raw response text if JSON decoding fails
            st.error(error_detail)
else:
    # Display chat history
    st.write("### Chat History:")
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="user-message"> {chat["user"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="assistant-message"> {chat["assistant"]}</div>', unsafe_allow_html=True)

    # Display an input field for the user to enter a question
    st.write("### Enter your legal question below:")
    user_question = st.text_input("Ask a question:", key="user_question")

    # Display the response when the user submits a question
    if st.button("Send"):
        if user_question:
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.post(
                "http://localhost:8000/chat/generate",
                json={"query": user_question, "user_id": st.session_state.user_id},
                headers=headers
            )
            if response.status_code == 200:
                assistant_response = response.json()["response"]

                # Append the new question and response to the chat history
                st.session_state.chat_history.append({
                    "user": user_question,
                    "assistant": assistant_response  # Extract the response text
                })

                st.rerun()
            else:
                st.error("Failed to get response from assistant")

    # Signout button in the sidebar
    with st.sidebar:
        if st.button("Sign Out"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.session_state.access_token = ""
            st.session_state.user_id = None
            st.rerun()

        # Retrieve user information
        st.write("### Get user information:")
        if st.button("Get User Info"):
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
            response = requests.get(f"http://localhost:8000/auth/users/{st.session_state.username}", headers=headers)
            if response.status_code == 200:
                user_info = response.json()
                st.write(f"Username: {user_info['username']}")
                st.write(f"Email: {user_info['email']}")
                st.write(f"Created At: {user_info['created_at']}")
            else:
                st.error(response.json()["detail"])