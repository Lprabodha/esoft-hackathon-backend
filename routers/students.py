from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.connection import get_db
from database import models
from schemas import student as student_schemas, skill as skill_schemas
from routers.auth import get_current_user # Import the dependency
from services.nlp_service import extract_skills_from_text # Import NLP service

router = APIRouter()

@router.get("/profiles/me", response_model=student_schemas.StudentProfileResponse)
def read_my_student_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get the current authenticated student's profile."""
    if not any(role.role.name == "student" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a student.")

    student_profile = db.query(models.StudentProfile).options(
        joinedload(models.StudentProfile.user),
        joinedload(models.StudentProfile.student_skills).joinedload(models.StudentSkill.skill)
    ).filter(models.StudentProfile.user_id == current_user.id).first()

    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")
    return student_profile

@router.post("/profiles/{user_id}/update", response_model=student_schemas.StudentProfileResponse)
def update_student_profile(
    user_id: int,
    profile_data: student_schemas.StudentProfileBase,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Update a student's profile. Only a student can update their own profile."""
    if user_id != current_user.id or not any(role.role.name == "student" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this profile.")

    student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Update fields
    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(student_profile, field, value)

    db.add(student_profile)
    db.commit()
    db.refresh(student_profile)
    return student_profile

@router.post("/profiles/{user_id}/extract-skills", response_model=List[skill_schemas.StudentSkillResponse])
def extract_and_add_skills_to_profile(
    user_id: int,
    text_to_analyze: str, # Could be resume content, project description, etc.
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Extracts skills from provided text using NLP and adds them to the student's profile.
    Only a student can update their own profile.
    """
    if user_id != current_user.id or not any(role.role.name == "student" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to modify this profile.")

    student_profile = db.query(models.StudentProfile).filter(models.StudentProfile.user_id == user_id).first()
    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    extracted_skill_names = [s['name'] for s in extract_skills_from_text(text_to_analyze)]
    added_skills = []

    for skill_name in extracted_skill_names:
        # Check if skill exists in our ontology, if not, create it (simplified for hackathon)
        db_skill = db.query(models.Skill).filter(models.Skill.name == skill_name).first()
        if not db_skill:
            db_skill = models.Skill(name=skill_name, category="Inferred") # Default category
            db.add(db_skill)
            db.commit()
            db.refresh(db_skill)

        # Check if student already has this skill
        existing_student_skill = db.query(models.StudentSkill).filter(
            models.StudentSkill.student_profile_id == student_profile.id,
            models.StudentSkill.skill_id == db_skill.id
        ).first()

        if not existing_student_skill:
            new_student_skill = models.StudentSkill(
                student_profile_id=student_profile.id,
                skill_id=db_skill.id,
                proficiency_level="intermediate", # Default, can be refined
                inferred_from="text_analysis"
            )
            db.add(new_student_skill)
            db.commit()
            db.refresh(new_student_skill)
            added_skills.append(new_student_skill)
        else:
            added_skills.append(existing_student_skill) # Include existing ones in response

    # Refresh the profile to get updated skills for the response model
    db.refresh(student_profile)
    # Manually load skills for the response model
    response_skills = []
    for ss in added_skills:
        db.refresh(ss) # Ensure relationship is loaded
        response_skills.append(skill_schemas.StudentSkillResponse(
            skill_id=ss.skill_id,
            proficiency_level=ss.proficiency_level,
            inferred_from=ss.inferred_from,
            skill=skill_schemas.SkillResponse.from_orm(ss.skill)
        ))

    return response_skills

# You can add endpoints for managing applications, learning paths here too