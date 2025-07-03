from pydantic import BaseModel
from typing import Optional, List
from schemas.opportunity import OpportunityResponse
from schemas.learning_resources import LearningResourceResponse
from schemas.skill import SkillResponse

class RecommendedOpportunity(BaseModel):
    opportunity: OpportunityResponse
    match_score: float
    missing_skills: List[SkillResponse]
    ai_reason: str # Why this recommendation?

class RecommendedLearningPath(BaseModel):
    learning_resource: LearningResourceResponse
    target_skill: SkillResponse
    ai_reason: str # Why this mission?

class CognitiveNavigatorRecommendations(BaseModel):
    recommended_opportunities: List[RecommendedOpportunity]
    recommended_learning_paths: List[RecommendedLearningPath]