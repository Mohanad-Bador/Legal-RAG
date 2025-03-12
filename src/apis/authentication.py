from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta 
from passlib.context import CryptContext
from sqlite3 import IntegrityError
from src.database.schema import get_user, insert_user
from src.database.models import UserRequest

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Secret key and algorithm for encoding and decoding JWT tokens
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# API router for authentication
router = APIRouter()

# Function to create an access token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Function to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# API endpoint for creating a new user
@router.post("/signup")
def sign_up(request: UserRequest):
    hashed_password = pwd_context.hash(request.password)
    try:
        insert_user(request.username, request.email, hashed_password)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")
    return {"message": "User created successfully"}

# API endpoint for login
@router.post("/login")
def login(request: OAuth2PasswordRequestForm = Depends()):
    user = get_user(request.username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not pwd_context.verify(request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password")
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

# API endpoint for getting user information
@router.get("/users/{username}")
def get_user_info(username: str, current_user: dict = Depends(get_current_user)):
    user = get_user(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user["username"], "email": user["email"], "created_at": user["created_at"]}

# API endpoint for getting the current active user
@router.get("/me", tags=["Users"])
def get_me(current_user: dict = Depends(get_current_user)):
    return current_user