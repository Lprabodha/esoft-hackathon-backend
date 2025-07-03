from pydantic import BaseModel
from typing import Optional, List
import datetime
from schemas.skill import OpportunityRequiredSkillCreate, OpportunityRequiredSkillResponse

class OpportunityBase(BaseModel):
    title: str
    description: str
    type: str  # You can replace with Literal if you want enum validation
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

class OpportunityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    department: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[datetime.date] = None
    end_date: Optional[datetime.date] = None
    application_deadline: Optional[datetime.datetime] = None
    num_positions: Optional[int] = None
    status: Optional[str] = None
    required_skills: Optional[List[OpportunityRequiredSkillCreate]] = None  # Optional update of skills

    class Config:
        from_attributes = True

class OpportunityResponse(OpportunityBase):
    id: int
    posted_by_user_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    required_skills: List[OpportunityRequiredSkillResponse] = []

    class Config:
        from_attributes = True
