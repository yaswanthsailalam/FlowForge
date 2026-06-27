import logging
from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pymongo.errors import PyMongoError, OperationFailure

from backend.app.core import security
from backend.app.core.config import settings
from backend.app.core.utils import utcnow, new_id, serialize_doc
from backend.app.db.mongodb import users_col, is_db_connected
from backend.app.schemas import User, UserCreate, Token

router = APIRouter()
logger = logging.getLogger(__name__)

def check_db_ready():
    if not is_db_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATABASE_UNAVAILABLE"
        )

@router.post("/register", response_model=User)
def register(user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    check_db_ready()

    # Normalized email: lowercase and stripped
    email = user_in.email.lower().strip()

    try:
        # Check duplicate
        if users_col.find_one({"email": email}):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="EMAIL_ALREADY_REGISTERED",
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

        # Explicit write check
        result = users_col.insert_one(user_dict)
        if not result.inserted_id:
            logger.error("Failed to insert user into MongoDB")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="PERSISTENCE_FAILURE"
            )

        logger.info(f"User registered successfully: {email}")
        return serialize_doc(user_dict)

    except OperationFailure as e:
        if "auth failed" in str(e).lower():
            logger.error("MongoDB authentication failure during registration")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="DATABASE_CONFIGURATION_ERROR"
            )
        raise e
    except PyMongoError as e:
        logger.error(f"Database error during registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DATABASE_ERROR"
        )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    check_db_ready()

    # Use normalized email for lookup
    email = form_data.username.lower().strip()

    try:
        user = users_col.find_one({"email": email})

        if not user or not security.verify_password(form_data.password, user["hashed_password"]):
            logger.warning(f"Failed login attempt for: {email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="INCORRECT_CREDENTIALS",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user.get("is_active", True):
            logger.warning(f"Login attempt for inactive user: {email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INACTIVE_USER"
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        token = security.create_access_token(
            user["user_id"], expires_delta=access_token_expires
        )

        logger.info(f"User logged in: {email}")
        return {
            "access_token": token,
            "token_type": "bearer",
        }
    except OperationFailure as e:
        if "auth failed" in str(e).lower():
            logger.error("MongoDB authentication failure during login")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="DATABASE_CONFIGURATION_ERROR"
            )
        raise e
    except PyMongoError as e:
        logger.error(f"Database error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="DATABASE_ERROR"
        )
