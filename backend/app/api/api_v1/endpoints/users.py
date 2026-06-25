from typing import Any
from fastapi import APIRouter, Depends
from backend.app.api import deps
from backend.app.schemas import User

router = APIRouter()

@router.get("/me", response_model=User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    Get current user.
    """
    return current_user
