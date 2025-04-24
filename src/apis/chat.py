from fastapi import APIRouter, Depends, HTTPException
from src.rag.RAG_Pipeline import dummy_rag_service, rag_service
from src.database.schema import insert_message, get_chat_history, get_user_chats, create_chat, update_chat_title, delete_chat, get_chat_by_id
from src.database.models import QueryRequest, ChatCreateRequest, ChatUpdateRequest, ChatResponse, ChatListResponse, ChatHistoryResponse
from src.apis.authentication import get_current_user
from datetime import datetime

router = APIRouter()

# API endpoint for creating a new chat
@router.post("/create", response_model=ChatResponse)
def create_new_chat(request: ChatCreateRequest, current_user: dict = Depends(get_current_user)):
    chat_id = create_chat(request.user_id, request.title)
    return ChatResponse(
        id=chat_id,
        title=request.title,
        created_at=datetime.now()
    )

# API endpoint for listing all chats
@router.get("/list/{user_id}", response_model=ChatListResponse)
def list_chats(user_id: int, current_user: dict = Depends(get_current_user)):
    if current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    chats = get_user_chats(user_id)
    chat_responses = [
        ChatResponse(
            id=chat["id"], 
            title=chat["title"], 
            created_at=chat["created_at"]
        ) for chat in chats
    ]
    return ChatListResponse(chats=chat_responses)

# API endpoint for updating chat title
@router.put("/update")
def update_chat(request: ChatUpdateRequest, current_user: dict = Depends(get_current_user)):
    update_chat_title(request.chat_id, request.title)
    return {"message": "Chat title updated successfully"}

# API endpoint for getting chat history
@router.get("/history/{chat_id}", response_model=ChatHistoryResponse)
def get_history(chat_id: int, current_user: dict = Depends(get_current_user)):
    messages = get_chat_history(chat_id)
    return ChatHistoryResponse(messages=messages)

# API endpoint for deleting a chat by ID
@router.delete("/{chat_id}")
def delete_chat_by_id(chat_id: int, current_user: dict = Depends(get_current_user)):
    # First check if the chat exists
    chat = get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # Then check if the chat belongs to the current user
    if chat['user_id'] != current_user['id']:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this chat")
    
    # If checks pass, delete the chat
    delete_chat(chat_id)
    return {"message": "Chat deleted successfully"}

# API endpoint for generating a response
@router.post("/generate_dummy")
def generate_dummy_response(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    # Create a new chat if chat_id is not provided
    chat_id = request.chat_id
    if not chat_id:
        chat_id = create_chat(request.user_id)
    
    # Generate response using dummy service for now
    response = dummy_rag_service.generate_response(request.query)
    model = request.model or "default_model"
    
    # Store the message in the database
    insert_message(chat_id, request.query, response, model)
    
    return {
        "response": response,
        "chat_id": chat_id
    }

@router.post("/generate")
def generate_response(request: QueryRequest, current_user: dict = Depends(get_current_user)):
    # Create a new chat if chat_id is not provided
    chat_id = request.chat_id
    if not chat_id:
        chat_id = create_chat(request.user_id)
    
    # Generate response using the real RAG service
    response = rag_service.generate_response(request.query)
    model = request.model or rag_service.llm_model_id
    
    # Store the message in the database
    insert_message(chat_id, request.query, response, model)
    
    return {
        "response": response,
        "chat_id": chat_id
    }