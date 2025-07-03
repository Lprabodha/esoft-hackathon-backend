# cognitive_navigator_backend/routers/faculty_orgs.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from database.connection import get_db
from database import models
from schemas import faculty_org as faculty_org_schemas
# from routers.auth import get_current_user # Not needed if public

router = APIRouter()

@router.get("/profiles/me", response_model=faculty_org_schemas.FacultyOrgProfileResponse)
# def read_my_faculty_org_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)): # OLD LINE
def read_my_faculty_org_profile(db: Session = Depends(get_db)): # NEW LINE: No current_user dependency
    """
    TEMPORARY: Get the first faculty/organization profile found in the database.
    In production, this would be `current_user`'s profile.
    """
    # For hackathon, just return the first faculty/org profile
    faculty_org_profile = db.query(models.FacultyOrgProfile).options(
        joinedload(models.FacultyOrgProfile.user)
    ).first() # Find ANY faculty/org profile

    if not faculty_org_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty/Organization profile not found. Please register at least one faculty/industry partner user.")
    return faculty_org_profile

@router.get("/profiles/{user_id}", response_model=faculty_org_schemas.FacultyOrgProfileResponse)
def read_faculty_org_profile(
    user_id: int,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(get_current_user) # OLD LINE
):
    """
    TEMPORARY: Get details of a specific faculty/organization profile by user ID.
    No authorization check for hackathon.
    """
    # if user_id != current_user.id and not any(role.role.name == "admin" for role in current_user.roles): # REMOVE THIS LINE
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this profile.") # REMOVE THIS LINE

    faculty_org_profile = db.query(models.FacultyOrgProfile).options(
        joinedload(models.FacultyOrgProfile.user)
    ).filter(models.FacultyOrgProfile.user_id == user_id).first()

    if not faculty_org_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty/Organization profile not found.")
    return faculty_org_profile

@router.post("/profiles/{user_id}/update", response_model=faculty_org_schemas.FacultyOrgProfileResponse)
def update_faculty_org_profile(
    user_id: int,
    profile_data: faculty_org_schemas.FacultyOrgProfileBase,
    db: Session = Depends(get_db),
    # current_user: models.User = Depends(get_current_user) # OLD LINE
):
    """
    TEMPORARY: Update a faculty/organization's profile. No authorization check for hackathon.
    """
    # if user_id != current_user.id and not any(role.role.name in ["faculty", "industry_partner", "admin"] for role in current_user.roles): # REMOVE THIS LINE
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this profile.") # REMOVE THIS LINE

    faculty_org_profile = db.query(models.FacultyOrgProfile).filter(models.FacultyOrgProfile.user_id == user_id).first()
    if not faculty_org_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Faculty/Organization profile not found.")

    # Update fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(faculty_org_profile, field, value)

    db.add(faculty_org_profile)
    db.commit()
    db.refresh(faculty_org_profile)

    # Eager load user for response
    faculty_org_profile = db.query(models.FacultyOrgProfile).options(
        joinedload(models.FacultyOrgProfile.user)
    ).filter(models.FacultyOrgProfile.id == faculty_org_profile.id).first()

    return faculty_org_profile