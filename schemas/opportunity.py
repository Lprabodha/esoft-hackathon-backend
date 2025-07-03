from pydantic import BaseModel
from typing import Optional, List
import datetime
from schemas.skill import SkillBase, OpportunityRequiredSkillCreate, OpportunityRequiredSkillResponse

class OpportunityBase(BaseModel):
    title: str
    description: str
    type: str # Use Literal for specific enums if needed
    department: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    application_deadline: datetime.datetime
    num_positions: Optional[int] = None
    status: Optional[str] = "open"

class OpportunityCreate(OpportunityBase):
    posted_by_user_id: int
    required_skills: Optional[List[OpportunityRequiredSkillCreate]] = []

class OpportunityResponse(OpportunityBase):
    id: int
    posted_by_user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    required_skills: List[OpportunityRequiredSkillResponse] = []

    class Config:
        from_attributes = True