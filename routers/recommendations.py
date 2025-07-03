from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from database.connection import get_db
from database import models
from schemas import recommendation as rec_schemas, skill as skill_schemas
from routers.auth import get_current_user
from services.nlp_service import SKILL_ONTOLOGY # Using the dummy ontology for now

router = APIRouter()

@router.get("/for-student/me", response_model=rec_schemas.CognitiveNavigatorRecommendations)
def get_cognitive_navigator_recommendations(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Provides AI-powered recommendations for opportunities and learning paths
    for the authenticated student.
    """
    if not any(role.role.name == "student" for role in current_user.roles):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is not a student.")

    student_profile = db.query(models.StudentProfile).options(
        joinedload(models.StudentProfile.student_skills).joinedload(models.StudentSkill.skill)
    ).filter(models.StudentProfile.user_id == current_user.id).first()

    if not student_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found.")

    student_current_skills = {ss.skill.name.lower() for ss in student_profile.student_skills if ss.skill}
    student_current_skill_ids = {ss.skill_id for ss in student_profile.student_skills}

    recommended_opportunities = []
    recommended_learning_paths = []

    # --- Opportunity Recommendations (Growth Zone Logic) ---
    all_opportunities = db.query(models.Opportunity).options(
        joinedload(models.Opportunity.required_skills).joinedload(models.OpportunityRequiredSkill.skill)
    ).filter(models.Opportunity.status == 'open').all()

    for opp in all_opportunities:
        required_skills_for_opp = {ors.skill.name.lower() for ors in opp.required_skills if ors.skill}
        required_skill_ids_for_opp = {ors.skill_id for ors in opp.required_skills}

        # Calculate possessed skills
        possessed_skills_for_opp = student_current_skills.intersection(required_skills_for_opp)

        # Calculate missing skills
        missing_skill_names = required_skills_for_opp - possessed_skills_for_opp
        missing_skills_objects = [
            skill_schemas.SkillResponse.from_orm(db.query(models.Skill).filter(models.Skill.name.ilike(s)).first())
            for s in missing_skill_names if db.query(models.Skill).filter(models.Skill.name.ilike(s)).first()
        ]

        # Simple match score (percentage of possessed required skills)
        match_score = (len(possessed_skills_for_opp) / len(required_skills_for_opp)) * 100 if required_skills_for_opp else 0

        # --- Cognitive Navigator Logic: Prioritize "Growth Zone" ---
        # For hackathon, a simple heuristic:
        # - High match score + few missing crucial skills (e.g., < 3 missing mandatory skills)
        # - Medium match score + clear learning path for missing skills
        # - Opportunities that align with student's interests (from profile)

        # Example heuristic: if a student has 70%+ of skills AND there are 1-2 missing skills
        # for which learning resources exist, it's a good growth opportunity.

        is_growth_opportunity = False
        ai_reason = "Based on your current skills."

        if 0 < len(missing_skill_names) <= 3 and match_score >= 50: # Example threshold
            # Check if learning resources exist for missing skills (simplified check)
            for missing_skill_name in missing_skill_names:
                db_missing_skill = db.query(models.Skill).filter(models.Skill.name.ilike(missing_skill_name)).first()
                if db_missing_skill:
                    resource_count = db.query(models.ResourceAssociatedSkill).filter(
                        models.ResourceAssociatedSkill.skill_id == db_missing_skill.id
                    ).count()
                    if resource_count > 0:
                        is_growth_opportunity = True
                        ai_reason = f"Recommended for growth in skills like '{missing_skill_name}' which are crucial for this role."
                        break # Found at least one resource for a missing skill

        # Add to recommendations if it's a good match or a growth opportunity
        if match_score >= 70 or is_growth_opportunity: # Example threshold
            recommended_opportunities.append(rec_schemas.RecommendedOpportunity(
                opportunity=opportunity_schemas.OpportunityResponse.from_orm(opp),
                match_score=round(match_score, 2),
                missing_skills=missing_skills_objects,
                ai_reason=ai_reason
            ))

    # Sort opportunities (e.g., by match score, then by growth potential)
    recommended_opportunities.sort(key=lambda x: x.match_score, reverse=True)


    # --- Learning Path Recommendations (Micro-Missions) ---
    # Identify skills the student *should* learn based on desired opportunities or general trends
    # For hackathon: Identify skills that are required by top recommended opportunities but missing.

    target_skills_for_learning = set()
    for rec_opp in recommended_opportunities[:5]: # Consider top 5 recommended opportunities
        for missing_skill in rec_opp.missing_skills:
            target_skills_for_learning.add(missing_skill.id)

    all_learning_resources = db.query(models.LearningResource).options(
        joinedload(models.LearningResource.associated_skills).joinedload(models.ResourceAssociatedSkill.skill)
    ).all()

    for resource in all_learning_resources:
        resource_skill_ids = {ras.skill_id for ras in resource.associated_skills}

        # If this resource helps with a target skill the student needs
        intersecting_target_skills = target_skills_for_learning.intersection(resource_skill_ids)

        if intersecting_target_skills:
            for skill_id in intersecting_target_skills:
                # Ensure student doesn't already have this skill
                if skill_id not in student_current_skill_ids:
                    db_target_skill = db.query(models.Skill).filter(models.Skill.id == skill_id).first()
                    if db_target_skill:
                        recommended_learning_paths.append(rec_schemas.RecommendedLearningPath(
                            learning_resource=rec_schemas.LearningResourceResponse.from_orm(resource),
                            target_skill=skill_schemas.SkillResponse.from_orm(db_target_skill),
                            ai_reason=f"This mission helps you acquire '{db_target_skill.name}', which is vital for opportunities you might be interested in."
                        ))

    # Deduplicate learning paths if a resource helps with multiple target skills
    unique_learning_paths = {}
    for lp in recommended_learning_paths:
        key = (lp.learning_resource.id, lp.target_skill.id)
        unique_learning_paths[key] = lp
    recommended_learning_paths = list(unique_learning_paths.values())


    return rec_schemas.CognitiveNavigatorRecommendations(
        recommended_opportunities=recommended_opportunities,
        recommended_learning_paths=recommended_learning_paths
    )