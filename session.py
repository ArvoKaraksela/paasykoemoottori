from pydantic import BaseModel, Field
from typing import Dict, Optional
from typing import List
from app.models.recommendation import TaskIn


class CreateSessionRequest(BaseModel):
    goal: str = Field(..., pattern="^(maximize_points|maximize_learning)$")
    remaining_time_min: int = Field(..., ge=0, le=10000)
    skill_by_topic: Dict[str, float] = Field(default_factory=dict)


class CreateSessionResponse(BaseModel):
    session_id: str


class SessionState(BaseModel):
    session_id: str
    goal: str
    remaining_time_min: int
    skill_by_topic: Dict[str, float]
    last_recommended_task_id: Optional[str] = None
    recommendation_count: int = 0
    choice_count: int = 0
    choice_compliance: float = 0.0
    time_compliance: float = 0.0


class ChoiceRequest(BaseModel):
    chosen_task_id: str
    time_spent_min: int = Field(..., ge=0, le=10000)

class SessionRecommendRequest(BaseModel):
    tasks: List[TaskIn] = Field(..., min_length=1)
