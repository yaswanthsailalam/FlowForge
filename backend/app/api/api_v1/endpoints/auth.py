from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import users_col
from backend.app.schemas import User, UserCreate, Token

router = APIRouter()

@router.post("/register", response_model=User)
def register(user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    # Normalized email
    email = user_in.email.lower().strip()

    # Check duplicate
    if users_col.find_one({"email": email}):
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists.",
        )

    user_id = new_id()
    user_dict = {
        "user_id": user_id,
        "email": email,
        "hashed_password": security.get_password_hash(user_in.password),
        "full_name": user_in.full_name,
        "is_active": True,
        "created_at": utcnow(),
        "updated_at": utcnow(),
    }
    users_col.insert_one(user_dict)

    return serialize_doc(user_dict)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    email = form_data.username.lower().strip()
    user = users_col.find_one({"email": email})

    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user["user_id"], expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
