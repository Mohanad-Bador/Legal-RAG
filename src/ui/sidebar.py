import streamlit as st
from api_helpers import fetch_user_chats, select_chat, update_chat_title, delete_user_chat, handle_logout

def render_sidebar():
    with st.sidebar:
        st.write(f"### Welcome, {st.session_state.username}!")
        
        # New Chat button - only creates UI placeholder, doesn't create in DB yet
        if st.button("➕ New Chat"):
            st.session_state.current_chat_id = None
            st.session_state.chat_history = []
            st.rerun()
            
        # Fetch and show chat list
        fetch_user_chats()
        if not st.session_state.chat_list:
            st.write("No chats available. Start a new chat!")
        else:
            st.write("### Your Chats:")
        
        # Display chat list
        for chat in st.session_state.chat_list:
            col1, col2, col3 = st.columns([3, 0.5, 0.5])
            
            # If we're editing this chat's title
            if st.session_state.editing_chat_title and st.session_state.current_chat_id == chat["id"]:
                # Using a form to edit the chat title
                with st.form(key=f"edit_form_{chat['id']}", clear_on_submit=False):
                    new_title = st.text_input("Edit title", value=chat["title"], key=f"edit_title_{chat['id']}")
                    submitted = st.form_submit_button("Save", use_container_width=True)
                    if submitted:
                        update_chat_title(chat["id"], new_title)
            else:
                # Regular chat button with edit and delete options
                with col1:
                    if st.button(chat["title"], key=f"chat_{chat['id']}", 
                                use_container_width=True, 
                                type="primary" if st.session_state.current_chat_id == chat["id"] else "secondary"):
                        select_chat(chat["id"])
                with col2:
                    if st.button("✏️", key=f"edit_{chat['id']}"):
                        st.session_state.editing_chat_title = True
                        st.session_state.current_chat_id = chat["id"]
                        st.rerun()
                with col3:
                    if st.button("🗑️", key=f"delete_{chat['id']}"):
                        delete_user_chat(chat["id"])
        
        # Signout button
        if st.button("Sign Out"):
            handle_logout()
