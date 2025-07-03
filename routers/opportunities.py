from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional

from database.connection import get_db
from database import models
from schemas import opportunity as opportunity_schemas
from routers.auth import get_current_user

router = APIRouter()

@router.post("/", response_model=opportunity_schemas.OpportunityResponse, status_code=status.HTTP_201_CREATED)
def create_opportunity(
    opportunity_data: opportunity_schemas.OpportunityCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Create a new opportunity. Only faculty/industry partners can post.
    """
    is_authorized = any(role.role.name in ["faculty", "industry_partner"] for role in current_user.roles)
    if not is_authorized:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only faculty or industry partners can post opportunities.")

    db_opportunity = models.Opportunity(
        posted_by_user_id=current_user.id,
        **opportunity_data.dict(exclude={"required_skills"})
    )
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)

    # Add required skills
    for skill_req in opportunity_data.required_skills:
        db_skill = db.query(models.Skill).filter(models.Skill.id == skill_req.skill_id).first()
        if not db_skill:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Skill with ID {skill_req.skill_id} not found.")

        opportunity_skill = models.OpportunityRequiredSkill(
            opportunity_id=db_opportunity.id,
            skill_id=skill_req.skill_id,
            is_mandatory=skill_req.is_mandatory
        )
        db.add(opportunity_skill)

    db.commit()
    db.refresh(db_opportunity)

    db_opportunity = db.query(models.Opportunity).options(
        joinedload(models.Opportunity.required_skills).joinedload(models.OpportunityRequiredSkill.skill)
    ).filter(models.Opportunity.id == db_opportunity.id).first()

    return db_opportunity

@router.get("/", response_model=List[opportunity_schemas.OpportunityResponse])
def get_all_opportunities(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = Query(None, description="Filter by opportunity type (internship, research, training)"),
    department: Optional[str] = Query(None, description="Filter by department"),
    location: Optional[str] = Query(None, description="Filter by location")
):
    """
    Get a list of all opportunities with optional filters.
    """
    query = db.query(models.Opportunity).options(
        joinedload(models.Opportunity.required_skills).joinedload(models.OpportunityRequiredSkill.skill)
    )

    if type:
        query = query.filter(models.Opportunity.type == type)
    if department:
        query = query.filter(models.Opportunity.department == department)
    if location:
        query = query.filter(models.Opportunity.location.ilike(f"%{location}%"))

    opportunities = query.offset(skip).limit(limit).all()
    return opportunities

@router.get("/{opportunity_id}", response_model=opportunity_schemas.OpportunityResponse)
def get_opportunity(opportunity_id: int, db: Session = Depends(get_db)):
    """
    Get details of a specific opportunity by ID.
    """
    opportunity = db.query(models.Opportunity).options(
        joinedload(models.Opportunity.required_skills).joinedload(models.OpportunityRequiredSkill.skill)
    ).filter(models.Opportunity.id == opportunity_id).first()

    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")
    return opportunity

@router.put("/{opportunity_id}", response_model=opportunity_schemas.OpportunityResponse)
def update_opportunity(
    opportunity_id: int,
    updated_data: opportunity_schemas.OpportunityUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Update an existing opportunity. Only the creator can update.
    """
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    if opportunity.posted_by_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this opportunity")

    for field, value in updated_data.dict(exclude_unset=True).items():
        setattr(opportunity, field, value)

    db.commit()
    db.refresh(opportunity)
    return opportunity

@router.delete("/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_opportunity(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Delete an opportunity. Only the creator can delete.
    """
    opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    if opportunity.posted_by_user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this opportunity")

    db.delete(opportunity)
    db.commit()
    return None
