import streamlit as st
import requests

# Streamlit app UI
st.title("Legal Document Retrieval with RAG")

# Display an input field for the user to enter a question
st.write("### Enter your legal question below:")
user_question = st.text_input("Ask a question:")

# Display the response when the user submits a question
if user_question:
    st.write("### Response:")
    response = requests.post(
        "http://localhost:8000/generate",
        json={"query": user_question}
    ).json()
    st.write(response["response"])

# User registration
st.write("### Register a new user:")
username = st.text_input("Username:")
email = st.text_input("Email:")

if st.button("Register"):
    response = requests.post(
        "http://localhost:8000/users",
        json={"username": username, "email": email}
    )
    if response.status_code == 200:
        st.success("User created successfully")
    else:
        st.error(response.json()["detail"])

# Retrieve user information
st.write("### Get user information:")
search_username = st.text_input("Search Username:")

if st.button("Get User Info"):
    response = requests.get(f"http://localhost:8000/users/{search_username}")
    if response.status_code == 200:
        user_info = response.json()
        st.write(f"Username: {user_info['username']}")
        st.write(f"Email: {user_info['email']}")
        st.write(f"Created At: {user_info['created_at']}")
    else:
        st.error(response.json()["detail"])