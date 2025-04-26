import streamlit as st
import requests

class APIHelper:
    BASE_URL = "http://127.0.0.1:8000"
    
    @staticmethod
    def get_headers():
        return {"Authorization": f"Bearer {st.session_state.access_token}"} if st.session_state.access_token else {}
    
    @classmethod
    def login(cls, username, password):
        response = requests.post(
            f"{cls.BASE_URL}/auth/login",
            data={"username": username, "password": password}
        )
        return response
    
    @classmethod
    def signup(cls, username, email, password):
        response = requests.post(
            f"{cls.BASE_URL}/auth/signup",
            json={"username": username, "email": email, "password": password}
        )
        return response
    
    @classmethod
    def fetch_chat_history(cls, chat_id):
        response = requests.get(
            f"{cls.BASE_URL}/chat/history/{chat_id}",
            headers=cls.get_headers()
        )
        return response
    
    @classmethod
    def fetch_user_chats(cls, user_id):
        response = requests.get(
            f"{cls.BASE_URL}/chat/list/{user_id}",
            headers=cls.get_headers()
        )
        return response
    
    @classmethod
    def create_chat(cls, user_id, title="New Chat"):
        response = requests.post(
            f"{cls.BASE_URL}/chat/create",
            json={"user_id": user_id, "title": title},
            headers=cls.get_headers()
        )
        return response
    
    @classmethod
    def update_chat_title(cls, chat_id, new_title):
        response = requests.put(
            f"{cls.BASE_URL}/chat/update",
            json={"chat_id": chat_id, "title": new_title},
            headers=cls.get_headers()
        )
        return response
    
    @classmethod
    def generate_response(cls, query, user_id, chat_id=None):
        response = requests.post(
            f"{cls.BASE_URL}/chat/generate",
            json={"query": query, "user_id": user_id, "chat_id": chat_id},
            headers=cls.get_headers()
        )
        return response

    @classmethod
    def delete_chat(cls, chat_id):
        response = requests.delete(
            f"{cls.BASE_URL}/chat/{chat_id}",
            headers=cls.get_headers()
        )
        return response

# UI Helper Functions
def fetch_chat_history(chat_id):
    if st.session_state.logged_in:
        response = APIHelper.fetch_chat_history(chat_id)
        if response.status_code == 200:
            st.session_state.chat_history = []
            user_message = None
            for message in response.json()["messages"]:
                if message["role"] == "human":
                    user_message = message["content"]
                elif message["role"] == "ai" and user_message:  # Ensure we have a user message
                    st.session_state.chat_history.append({
                        "user": user_message,
                        "assistant": message["content"]
                    })
                    user_message = None  # Reset for next pair

def fetch_user_chats():
    if st.session_state.logged_in and st.session_state.user_id:
        response = APIHelper.fetch_user_chats(st.session_state.user_id)
        if response.status_code == 200:
            st.session_state.chat_list = response.json()["chats"]

def create_new_chat(title="New Chat"):
    if st.session_state.logged_in and st.session_state.user_id:
        response = APIHelper.create_chat(st.session_state.user_id, title)
        if response.status_code == 200:
            new_chat = response.json()
            st.session_state.current_chat_id = new_chat["id"]
            st.session_state.chat_history = []
            fetch_user_chats()  # Refresh chat list
            return new_chat["id"]
        return None

def update_chat_title(chat_id, new_title):
    if st.session_state.logged_in:
        response = APIHelper.update_chat_title(chat_id, new_title)
        if response.status_code == 200:
            fetch_user_chats()  # Refresh chat list
            st.session_state.editing_chat_title = False
            st.rerun()

def delete_user_chat(chat_id):
    if st.session_state.logged_in:
        response = APIHelper.delete_chat(chat_id)
        if response.status_code == 200:
            fetch_user_chats()  # Refresh chat list
            # If we're deleting the current chat, reset the current chat
            if st.session_state.current_chat_id == chat_id:
                st.session_state.current_chat_id = None
                st.session_state.chat_history = []
            st.rerun()

def select_chat(chat_id):
    st.session_state.current_chat_id = chat_id
    fetch_chat_history(chat_id)
    st.rerun()

def handle_login(username, password):
    response = APIHelper.login(username, password)
    if response.status_code == 200:
        data = response.json()
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.access_token = data["access_token"]
        st.session_state.user_id = data["user_id"]
        fetch_user_chats()  # Load chats after login
        return True, "Logged in successfully"
    return False, "Invalid username or password"

def handle_signup(username, email, password):
    response = APIHelper.signup(username, email, password)
    if response.status_code == 200:
        data = response.json()
        st.session_state.logged_in = True
        st.session_state.username = username
        st.session_state.user_id = data["user_id"]
        st.session_state.access_token = data["access_token"]
        return True, "User created successfully"
    try:
        error_detail = response.json().get("detail", "Unknown error")
    except ValueError:
        error_detail = response.text
    return False, error_detail

def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.access_token = ""
    st.session_state.user_id = None
    st.session_state.current_chat_id = None
    st.session_state.chat_list = []
    st.session_state.chat_history = []
    st.rerun()

def handle_user_question(user_question):
    # Create a new chat if none is selected
    if not st.session_state.current_chat_id:
        # First message creates the chat with the first few words as the title
        chat_title = user_question[:20] + "..." if len(user_question) > 20 else user_question
        chat_id = create_new_chat(title=chat_title)
        if not chat_id:
            return False, "Failed to create new chat"
    
    # Display the new user message immediately
    with st.chat_message("user"):
        st.write(user_question)
    
    # Create a message container for the assistant response
    assistant_message = st.chat_message("assistant")
    
    # Create a placeholder within the assistant message container
    with assistant_message:
        response_placeholder = st.empty()
        response_placeholder.info("Getting response...")
    
    response = APIHelper.generate_response(
        user_question, 
        st.session_state.user_id, 
        st.session_state.current_chat_id
    )
    
    if response.status_code == 200:
        data = response.json()
        assistant_response = data["answer"]
        
        # Update the assistant message with the response
        with assistant_message:
            response_placeholder.empty()
            st.write(assistant_response)
        
        # Append the new question and response to the chat history
        st.session_state.chat_history.append({
            "user": user_question,
            "assistant": assistant_response
        })
        
        # Check if this is the first message in the chat history then rerun to refresh the chat list
        if len(st.session_state.chat_history) == 1:
            st.rerun()
            
        return True, None
    else:
        # Update placeholder with error message
        with assistant_message:
            response_placeholder.empty()  # Clear the loading message
            st.error("Failed to get response from assistant")
        return False, "Failed to get response from assistant"
