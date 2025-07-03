from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.connection import get_db
from database import models
from schemas import user as user_schemas
from routers.auth import get_current_user # Import the dependency

router = APIRouter()

@router.get("/me", response_model=user_schemas.UserInDB)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get the current authenticated user's details."""
    return current_user

@router.get("/{user_id}", response_model=user_schemas.UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    """Get details of a specific user by ID (admin/self access)."""
    # Basic authorization: allow user to see their own profile or admin to see any
    if user_id != current_user.id and not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this user.")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

# You can add update user profile endpoints here