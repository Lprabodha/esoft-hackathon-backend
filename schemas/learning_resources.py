from pydantic import BaseModel
from typing import Optional, List
import datetime
from schemas.skill import SkillResponse

class LearningResourceBase(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    type: Optional[str] = None
    estimated_time_to_complete_min: Optional[int] = None
    difficulty_level: Optional[str] = None

class LearningResourceCreate(LearningResourceBase):
    associated_skill_ids: Optional[List[int]] = []

class LearningResourceResponse(LearningResourceBase):
    id: int
    created_at: datetime.datetime
    associated_skills: List[SkillResponse] = [] # List of associated skills

    class Config:
        orm_mode = True