from pydantic import BaseModel
from typing import Optional, List
from schemas.user import UserInDB
from schemas.skill import SkillBase, StudentSkillCreate, StudentSkillResponse

class StudentProfileBase(BaseModel):
    academic_id: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    gpa: Optional[float] = None
    bio: Optional[str] = None
    interests: Optional[str] = None # Or List[str] if parsing to JSON
    resume_url: Optional[str] = None
    profile_picture_url: Optional[str] = None

class StudentProfileCreate(StudentProfileBase):
    user_id: int
    skills: Optional[List[StudentSkillCreate]] = []

class StudentProfileResponse(StudentProfileBase):
    id: int
    user: UserInDB # Nested user data
    skills: List[StudentSkillResponse] = [] # Nested student skills

    class Config:
        from_attributes = True