# cognitive_navigator_backend/schemas/faculty_org.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from schemas.user import UserInDB # Assuming you want to nest user data in response

class FacultyOrgProfileBase(BaseModel):
    organization_name: Optional[str] = None
    department: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    website_url: Optional[str] = None
    description: Optional[str] = None

class FacultyOrgProfileCreate(FacultyOrgProfileBase):
    # When creating, we'll link it to an existing user_id
    user_id: int

class FacultyOrgProfileResponse(FacultyOrgProfileBase):
    id: int
    user: UserInDB # Nested user details
    
    class Config:
        from_attributes = True # Pydantic V2