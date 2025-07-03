from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Date, DECIMAL, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import JSON # For MySQL JSON type
from .connection import Base
import datetime

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    roles = relationship("UserRole", back_populates="user")
    student_profile = relationship("StudentProfile", back_populates="user", uselist=False)
    faculty_org_profile = relationship("FacultyOrgProfile", back_populates="user", uselist=False)
    posted_opportunities = relationship("Opportunity", back_populates="posted_by_user")
    notifications = relationship("Notification", back_populates="user")
    feedback_given = relationship("Feedback", foreign_keys="[Feedback.from_user_id]", back_populates="from_user")
    feedback_received = relationship("Feedback", foreign_keys="[Feedback.to_user_id]", back_populates="to_user")
    user_actions = relationship("UserActionLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False) # e.g., 'student', 'faculty', 'industry_partner', 'admin'
    description = Column(Text)

    user_roles = relationship("UserRole", back_populates="role")

class UserRole(Base):
    __tablename__ = "user_roles"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="user_roles")

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    academic_id = Column(String(100), unique=True)
    department = Column(String(100))
    major = Column(String(100))
    gpa = Column(DECIMAL(3, 2))
    bio = Column(Text)
    interests = Column(Text) # Can be comma-separated or JSON string
    resume_url = Column(String(255))
    profile_picture_url = Column(String(255))

    user = relationship("User", back_populates="student_profile")
    student_skills = relationship("StudentSkill", back_populates="student_profile")
    applications = relationship("StudentApplication", back_populates="student_profile")
    learning_paths = relationship("StudentLearningPath", back_populates="student_profile")

class FacultyOrgProfile(Base):
    __tablename__ = "faculty_org_profiles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    organization_name = Column(String(255))
    department = Column(String(100))
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    website_url = Column(String(255))
    description = Column(Text)

    user = relationship("User", back_populates="faculty_org_profile")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(100))
    parent_skill_id = Column(Integer, ForeignKey("skills.id")) # Self-referencing

    parent_skill = relationship("Skill", remote_side=[id], back_populates="child_skills")
    child_skills = relationship("Skill", back_populates="parent_skill")
    student_skills = relationship("StudentSkill", back_populates="skill")
    opportunity_requirements = relationship("OpportunityRequiredSkill", back_populates="skill")
    resource_associations = relationship("ResourceAssociatedSkill", back_populates="skill")
    target_learning_paths = relationship("StudentLearningPath", back_populates="target_skill")


class StudentSkill(Base):
    __tablename__ = "student_skills"
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    proficiency_level = Column(Enum('beginner', 'intermediate', 'advanced', 'expert'))
    inferred_from = Column(String(255)) # e.g., 'resume_upload', 'project_id_123'

    student_profile = relationship("StudentProfile", back_populates="student_skills")
    skill = relationship("Skill", back_populates="student_skills")

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(Integer, primary_key=True, index=True)
    posted_by_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    type = Column(Enum('internship', 'research', 'training'), nullable=False)
    department = Column(String(100))
    location = Column(String(255))
    start_date = Column(Date)
    end_date = Column(Date)
    application_deadline = Column(DateTime, nullable=False)
    num_positions = Column(Integer)
    status = Column(Enum('open', 'closed', 'archived'), default='open')
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    posted_by_user = relationship("User", back_populates="posted_opportunities")
    required_skills = relationship("OpportunityRequiredSkill", back_populates="opportunity")
    applications = relationship("StudentApplication", back_populates="opportunity")

class OpportunityRequiredSkill(Base):
    __tablename__ = "opportunity_required_skills"
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)
    is_mandatory = Column(Boolean, default=True)

    opportunity = relationship("Opportunity", back_populates="required_skills")
    skill = relationship("Skill", back_populates="opportunity_requirements")

class StudentApplication(Base):
    __tablename__ = "student_applications"
    id = Column(Integer, primary_key=True, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=False)
    application_status = Column(Enum('applied', 'under_review', 'shortlisted', 'interview', 'accepted', 'rejected', 'withdrawn'),
                                nullable=False, default='applied')
    applied_at = Column(DateTime, default=datetime.datetime.now)
    cover_letter_url = Column(String(255))
    submission_details = Column(JSON) # For MySQL 5.7.8+

    student_profile = relationship("StudentProfile", back_populates="applications")
    opportunity = relationship("Opportunity", back_populates="applications")
    feedback = relationship("Feedback", back_populates="related_application", uselist=False)

class LearningResource(Base):
    __tablename__ = "learning_resources"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    url = Column(String(255), unique=True, nullable=False)
    type = Column(Enum('course', 'webinar', 'article', 'tutorial', 'book'))
    estimated_time_to_complete_min = Column(Integer)
    difficulty_level = Column(Enum('beginner', 'intermediate', 'advanced'))
    created_at = Column(DateTime, default=datetime.datetime.now)

    associated_skills = relationship("ResourceAssociatedSkill", back_populates="resource")
    learning_paths = relationship("StudentLearningPath", back_populates="resource")

class ResourceAssociatedSkill(Base):
    __tablename__ = "resource_associated_skills"
    resource_id = Column(Integer, ForeignKey("learning_resources.id", ondelete="CASCADE"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True)

    resource = relationship("LearningResource", back_populates="associated_skills")
    skill = relationship("Skill", back_populates="resource_associations")

class StudentLearningPath(Base):
    __tablename__ = "student_learning_paths"
    id = Column(Integer, primary_key=True, index=True)
    student_profile_id = Column(Integer, ForeignKey("student_profiles.id", ondelete="CASCADE"), nullable=False)
    resource_id = Column(Integer, ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False)
    target_skill_id = Column(Integer, ForeignKey("skills.id", ondelete="SET NULL")) # Skill this mission aims to develop
    status = Column(Enum('assigned', 'in_progress', 'completed', 'skipped'), default='assigned')
    assigned_at = Column(DateTime, default=datetime.datetime.now)
    completed_at = Column(DateTime)
    notes = Column(Text) # e.g., AI explanation for recommendation

    student_profile = relationship("StudentProfile", back_populates="learning_paths")
    resource = relationship("LearningResource", back_populates="learning_paths")
    target_skill = relationship("Skill", back_populates="target_learning_paths")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(100), nullable=False) # e.g., 'application_status_update', 'new_recommendation'
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    related_entity_id = Column(Integer) # e.g., application_id, opportunity_id

    user = relationship("User", back_populates="notifications")

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    to_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    related_application_id = Column(Integer, ForeignKey("student_applications.id", ondelete="SET NULL"))
    rating = Column(Integer) # e.g., 1-5 scale
    comments = Column(Text)
    feedback_date = Column(DateTime, default=datetime.datetime.now)

    from_user = relationship("User", foreign_keys=[from_user_id], back_populates="feedback_given")
    to_user = relationship("User", foreign_keys=[to_user_id], back_populates="feedback_received")
    related_application = relationship("StudentApplication", back_populates="feedback")

class UserActionLog(Base):
    __tablename__ = "user_actions_log"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    action_type = Column(String(100), nullable=False) # e.g., 'opportunity_view', 'resource_clicked'
    entity_type = Column(String(100)) # e.g., 'opportunity', 'resource', 'skill'
    entity_id = Column(Integer)
    timestamp = Column(DateTime, default=datetime.datetime.now)

    user = relationship("User", back_populates="user_actions")