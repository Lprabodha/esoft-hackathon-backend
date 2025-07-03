# cognitive_navigator_backend/routers/pdf_generator.py
import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
import pdfkit
import io

# Import auth dependency if you want to protect this endpoint
from routers.auth import get_current_user
from database import models
from database.connection import get_db
from sqlalchemy.orm import Session, joinedload

router = APIRouter()

# --- Jinja2 Environment Setup ---
# Points Jinja2 to the 'templates' directory relative to the project root
templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'templates')
jinja_env = Environment(
    loader=FileSystemLoader(templates_dir),
    autoescape=select_autoescape(['html', 'xml'])
)

# --- PDFKit Configuration (Adjust path for wkhtmltopdf) ---
# IMPORTANT: Replace this with the actual path to wkhtmltopdf.exe/binary on your system
# For Linux/macOS, if wkhtmltopdf is in PATH, you might not need to specify the path.
# Example for Windows: r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
# Example for Linux/macOS (if not in PATH): "/usr/local/bin/wkhtmltopdf"
# WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", "/usr/local/bin/wkhtmltopdf") # Default for common Linux/macOS
WKHTMLTOPDF_PATH = os.getenv("WKHTMLTOPDF_PATH", "/usr/local/bin/wkhtmltopdf")
pdfkit_config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
# --- Pydantic Schema for CV Data (Matches your sample data structure) ---
class ExperienceItem(BaseModel):
    role: str
    company: str
    location: str
    years: str
    details: List[str]

class EducationItem(BaseModel):
    degree: str
    institution: str
    year: str

class ProjectItem(BaseModel):
    name: str
    description: str
    link: str

class CvDataSchema(BaseModel):
    name: str
    title: str
    email: EmailStr
    phone: str
    address: str
    linkedin: str
    github: str
    summary: str
    skills: List[str]
    experience: List[ExperienceItem]
    education: List[EducationItem]
    projects: List[ProjectItem]
    certifications: List[str]

# --- Helper function to fetch student CV data from DB (example) ---
def get_student_cv_data(student_profile: models.StudentProfile) -> CvDataSchema:
    """
    Constructs CV data from a StudentProfile model for PDF generation.
    This is a simplified mapping; you'd expand it based on your DB model.
    """
    user = student_profile.user
    
    # Example: Map student_skills to a simple list of skill names
    skills_list = [ss.skill.name for ss in student_profile.student_skills if ss.skill]

    # Dummy data for experience, education, projects, certifications if not in DB yet
    # You'd fetch these from related tables (e.g., student_projects, student_education, etc.)
    # For hackathon, might need to hardcode or simplify if DB isn't fully populated.
    
    # For demonstration, using placeholder for complex fields if not available
    # In a real app, you'd have dedicated tables for these and fetch them.
    experience_data = [
        ExperienceItem(
            role="Student Research Assistant",
            company=user.first_name + "'s University",
            location=student_profile.department or "N/A",
            years="2023 - Present",
            details=["Assisted professor with research project.", "Analyzed data and prepared reports."]
        )
    ] if not student_profile.bio else [] # Placeholder if no real data

    education_data = [
        EducationItem(
            degree=student_profile.major or "N/A",
            institution="Your University Name", # Replace with actual university name
            year=student_profile.academic_id or "N/A" # Using academic_id as placeholder for year
        )
    ] if student_profile.major else []

    projects_data = [] # You'd fetch from a student_projects table
    certifications_data = [] # You'd fetch from a student_certifications table


    return CvDataSchema(
        name=f"{user.first_name} {user.last_name}",
        title=student_profile.major or "Student", # Use major as title for now
        email=user.email,
        phone="+1-XXX-XXX-XXXX", # Placeholder
        address="University Campus, City, Country", # Placeholder
        linkedin=f"linkedin.com/in/{user.first_name.lower()}{user.last_name.lower()}", # Placeholder
        github=f"github.com/{user.first_name.lower()}{user.last_name.lower()}", # Placeholder
        summary=student_profile.bio or "A dedicated student pursuing academic and professional growth.",
        skills=skills_list,
        experience=experience_data,
        education=education_data,
        projects=projects_data,
        certifications=certifications_data
    )


# --- FastAPI Endpoint ---
@router.get("/generate-cv-pdf/{user_id}", response_class=FileResponse)
async def generate_cv_pdf(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user) # Protect this endpoint
):
    """
    Generates a PDF CV for a given user ID.
    Requires authentication. Only a student can generate their own CV,
    or an admin/faculty can generate for others (add more robust auth).
    """
    # Basic authorization: student can get their own CV, admin can get any
    if user_id != current_user.id and not any(role.role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to generate this CV.")

    # Fetch student profile and related user data
    student_profile = db.query(models.StudentProfile).options(
        joinedload(models.StudentProfile.user),
        joinedload(models.StudentProfile.student_skills).joinedload(models.StudentSkill.skill)
    ).filter(models.StudentProfile.user_id == user_id).first()

    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    # Prepare data for the template
    cv_data_for_template = get_student_cv_data(student_profile)

    # Render HTML from template
    template = jinja_env.get_template("cv_template.html")
    html_content = template.render(cv_data_for_template.dict())

    # Convert HTML to PDF
    try:
        # Convert HTML to PDF. Pass False as the output argument to get bytes directly.
        pdf_bytes = pdfkit.from_string(html_content, False, configuration=pdfkit_config, options={'enable-local-file-access': None})
        
        # Create a BytesIO buffer from the returned bytes
        pdf_output = io.BytesIO(pdf_bytes)
        pdf_output.seek(0) # Rewind the buffer to the beginning

        filename = f"{cv_data_for_template.name.replace(' ', '_')}_CV.pdf"
        
        # Return as StreamingResponse
        return StreamingResponse(pdf_output, media_type="application/pdf", headers={
            "Content-Disposition": f"attachment; filename={filename}"
        })

    except Exception as e:
        # Catch errors from wkhtmltopdf (e.g., if it's not installed or path is wrong)
        print(f"Error generating PDF: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate PDF. Ensure wkhtmltopdf is installed and configured correctly. Error: {e}"
        )