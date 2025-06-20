import streamlit as st
import json
import os
import tempfile
from datetime import datetime, timedelta


class SessionManager:
    def __init__(self):
        # Create a session directory in temp folder
        self.session_dir = os.path.join(tempfile.gettempdir(), "legal_rag_sessions")
        os.makedirs(self.session_dir, exist_ok=True)
        
        # Creates a single session file for the current user
        self.session_file = os.path.join(self.session_dir, "current_session.json")
    
    def save_user_session(self, user_data):
        """Save user session data to file"""
        expires_at = datetime.now() + timedelta(days=7)
        
        session_data = {
            'logged_in': True,
            'username': user_data.get('username'),
            'access_token': user_data.get('access_token'),
            'user_id': user_data.get('user_id'),
            'current_chat_id': user_data.get('current_chat_id'),
            'expires_at': expires_at.isoformat()
        }
        
        try:
            with open(self.session_file, 'w') as f:
                json.dump(session_data, f)
        except Exception as e:
            pass
    
    def update_current_chat(self, chat_id):
        """Update only the current chat ID in the session"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                session_data['current_chat_id'] = chat_id
                
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f)
        except Exception as e:
            pass
    
    def load_user_session(self):
        """Load user session from file"""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                # Check if session is still valid
                expires_at = datetime.fromisoformat(session_data['expires_at'])
                if datetime.now() < expires_at:
                    return session_data
                else:
                    self.clear_user_session()
                    return None
            return None
        except Exception as e:
            return None
    
    def clear_user_session(self):
        """Clear user session file"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            pass
    
    def is_session_valid(self):
        """Check if current session is valid"""
        session_data = self.load_user_session()
        return session_data is not None

def initialize_session_state():
    """Initialize session state variables with default values"""
    defaults = {
        'chat_history': [],
        'logged_in': False,
        'username': "",
        'access_token': "",
        'user_id': None,
        'user_question': "",
        'should_clear_input': False,
        'current_chat_id': None,
        'chat_list': [],
        'editing_chat_title': False,
        'show_about_modal': False,
        'show_signup_modal': False,
        'session_loaded': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def load_persistent_session():
    """Load persistent session data from file storage"""
    if not st.session_state.session_loaded:
        # Initialize session manager if not already done
        if 'session_manager' not in st.session_state:
            st.session_state.session_manager = SessionManager()
        
        session_data = st.session_state.session_manager.load_user_session()
        if session_data:
            # Restore session data
            st.session_state.logged_in = session_data.get('logged_in', False)
            st.session_state.username = session_data.get('username', "")
            st.session_state.access_token = session_data.get('access_token', "")
            st.session_state.user_id = session_data.get('user_id', None)
            
            # Restore current chat if available
            current_chat_id = session_data.get('current_chat_id')
            if current_chat_id:
                st.session_state.current_chat_id = current_chat_id
            
            # Fetch user data if logged in
            if st.session_state.logged_in:
                from api_helpers import fetch_user_chats, fetch_chat_history
                fetch_user_chats()
                
                # Load chat history for the current chat
                if current_chat_id:
                    fetch_chat_history(current_chat_id)
        
        st.session_state.session_loaded = True