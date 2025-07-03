from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database.connection import get_db
from database import models
from schemas import auth as auth_schemas, user as user_schemas, oauth2_scheme
from utils.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

@router.post("/register", response_model=user_schemas.UserInDB, status_code=status.HTTP_201_CREATED)
def register_user(user_data: auth_schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user with email already exists
    db_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash password
    hashed_password = get_password_hash(user_data.password)

    # Create user
    new_user = models.User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Assign role (simplified for hackathon)
    db_role = db.query(models.Role).filter(models.Role.name == user_data.role_name).first()
    if not db_role:
        # Create role if it doesn't exist (for initial setup)
        db_role = models.Role(name=user_data.role_name, description=f"Role for {user_data.role_name}")
        db.add(db_role)
        db.commit()
        db.refresh(db_role)

    user_role = models.UserRole(user_id=new_user.id, role_id=db_role.id)
    db.add(user_role)
    db.commit()

    # Create profile based on role (simplified for hackathon)
    if user_data.role_name == "student":
        student_profile = models.StudentProfile(user_id=new_user.id)
        db.add(student_profile)
        db.commit()
    elif user_data.role_name in ["faculty", "industry_partner"]:
        faculty_org_profile = models.FacultyOrgProfile(user_id=new_user.id)
        db.add(faculty_org_profile)
        db.commit()

    return new_user

@router.post("/token", response_model=auth_schemas.Token)
def login_for_access_token(user_data: auth_schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Dependency to get current user (for protected routes)
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)): # Use oauth2_scheme directly
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = auth_schemas.decode_access_token(token) # auth_schemas is still needed for decode_access_token
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    user_id: int = payload.get("user_id")
    if email is None or user_id is None:
        raise credentials_exception
    token_data = auth_schemas.TokenData(email=email)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user

# This is a placeholder for `oauth2_scheme` that should be defined in schemas/auth.py
# Add this to schemas/auth.py:
# from fastapi.security import OAuth2PasswordBearer
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")