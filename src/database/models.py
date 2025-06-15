from pydantic import BaseModel
from typing import Optional, List, Union
from datetime import datetime

# Request models
class QueryRequest(BaseModel):
    query: str
    user_id: int
    chat_id: Optional[int] = None
    model: Optional[str] = None

class UserRequest(BaseModel):
    username: str
    email: str
    password: str

# New chat-related models
class ChatCreateRequest(BaseModel):
    user_id: int
    title: Optional[str] = "New Chat"

class ChatUpdateRequest(BaseModel):
    chat_id: int
    title: str

# Response models
class ChatResponse(BaseModel):
    id: int
    title: str
    created_at: datetime

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

class MessageResponse(BaseModel):
    role: str
    content: str
    contexts: List[List[str]]  = None

class ChatHistoryResponse(BaseModel):
    messages: List[Union[dict, MessageResponse]]