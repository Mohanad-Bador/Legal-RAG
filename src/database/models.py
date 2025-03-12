from pydantic import BaseModel

# Request models
class QueryRequest(BaseModel):
    query: str
    session_id: str = None
    user_id: int

class UserRequest(BaseModel):
    username: str
    email: str
    password: str