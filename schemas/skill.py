from pydantic import BaseModel
from typing import Optional, List

class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    parent_skill_id: Optional[int] = None

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: int
    class Config:
        from_attributes = True

class StudentSkillBase(BaseModel):
    skill_id: int
    proficiency_level: Optional[str] = None
    inferred_from: Optional[str] = None

class StudentSkillCreate(StudentSkillBase):
    pass

class StudentSkillResponse(StudentSkillBase):
    skill: SkillResponse # Nested skill details
    class Config:
        from_attributes = True

class OpportunityRequiredSkillBase(BaseModel):
    skill_id: int
    is_mandatory: Optional[bool] = True

class OpportunityRequiredSkillCreate(OpportunityRequiredSkillBase):
    pass

class OpportunityRequiredSkillResponse(OpportunityRequiredSkillBase):
    skill: SkillResponse # Nested skill details
    class Config:
        from_attributes = True