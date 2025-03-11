from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.RAG_Pipeline import rag_service
from src.db_utils import insert_application_logs, get_chat_history, insert_user, get_user
import uuid
import json

app = FastAPI()

# Request models
class QueryRequest(BaseModel):
    query: str
    session_id: str = None

class UserRequest(BaseModel):
    username: str
    email: str

@app.post("/generate")
def generate_response(request: QueryRequest):
    session_id = request.session_id or str(uuid.uuid4())
    response = rag_service.generate_response(request.query)
    response_str = json.dumps(response)  # Convert response to JSON string
    insert_application_logs(session_id, request.query, response_str, rag_service.llm_model_id)
    return {"response": response, "session_id": session_id}

@app.post("/users")
def create_user(request: UserRequest):
    try:
        insert_user(request.username, request.email)
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "User created successfully"}

@app.get("/users/{username}")
def get_user_info(username: str):
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user["username"], "email": user["email"], "created_at": user["created_at"]}

@app.get("/history/{session_id}")
def get_history(session_id: str):
    history = get_chat_history(session_id)
    return {"history": history}

@app.get("/")
def home():
    return {"message": "FastAPI RAG API is running!"}