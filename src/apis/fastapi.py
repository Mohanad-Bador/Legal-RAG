from fastapi import FastAPI
from src.apis.authentication import router as auth_router
from src.apis.chat import router as chat_router

# Create a FastAPI instance
app = FastAPI()

# Include the API routers
app.include_router(auth_router, prefix="/auth", tags=["User"])
# Include the chat router
app.include_router(chat_router, prefix="/chat", tags=["Chat"])

# API endpoint for homepage
@app.get("/")
def home():
    return {"message": "FastAPI RAG API is running!"}