import uuid
import json
from fastapi import APIRouter, Depends
from src.rag.RAG_Pipeline import dummy_rag_service, rag_service
from src.database.schema import insert_application_logs, get_chat_history, get_all_chats
from src.database.models import QueryRequest
from src.apis.authentication import get_current_user

router = APIRouter()

# API endpoint for generating a response
@router.post("/generate")
def generate_response(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    session_id = request.session_id or str(uuid.uuid4())
    response = rag_service.generate_response(request.query)
    response_str = json.dumps(response)  # Convert response to JSON string
    insert_application_logs(session_id, request.user_id, request.query, response_str, rag_service.llm_model_id)
    return {"response": response, "session_id": session_id}

# Dummy API endpoint for generating a response
@router.post("/generate")
def generate_dummy_response(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    session_id = request.session_id or str(uuid.uuid4())
    response = dummy_rag_service.generate_response(request.query)
    insert_application_logs(session_id, request.user_id, request.query, response, "Test")
    return {"response": response, "session_id": session_id}

# API endpoint for getting chat history
@router.get("/history/{user_id}/{session_id}")
def get_history(session_id: str, user_id: int, current_user: dict = Depends(get_current_user)):
    history = get_chat_history(session_id, user_id)
    return {"history": history}

# API endpoint for getting all chats
@router.get("/history/{user_id}")
def get_all_history(user_id: int, current_user: dict = Depends(get_current_user)):
    history = get_all_chats(user_id)
    return {"all chats": history}