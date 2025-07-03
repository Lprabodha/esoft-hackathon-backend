# cognitive_navigator_backend/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from database.connection import get_db
from database import models
from schemas import auth as auth_schemas, user as user_schemas, oauth2_scheme # Keep oauth2_scheme for now, though not used for auth
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

# --- TEMPORARY: Dummy get_current_user for hackathon to disable authentication ---
# In a real app, this would validate the JWT token.
def get_current_user(db: Session = Depends(get_db)):
    """
    TEMPORARY: This function bypasses actual JWT validation for hackathon purposes.
    It returns the first student user found, or raises an error if no student exists.
    """
    # Find the first user with the 'student' role
    student_role = db.query(models.Role).filter(models.Role.name == "student").first()
    if not student_role:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No 'student' role found in DB. Please register at least one student user.")

    # Find a user associated with the student role
    user_role_entry = db.query(models.UserRole).filter(models.UserRole.role_id == student_role.id).first()
    if not user_role_entry:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="No student users found. Please register at least one student.")

    user = db.query(models.User).filter(models.User.id == user_role_entry.user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Student user not found after role lookup.")

    # Load roles for the dummy user if needed by other functions
    user.roles # Accessing the relationship to load it

    return user