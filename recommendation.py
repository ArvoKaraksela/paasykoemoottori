from pydantic import BaseModel, Field
from typing import List


class TaskIn(BaseModel):
    id: str = Field(..., description="Task identifier")
    topic: str = Field(..., description="Topic/category key, e.g. chem_acid_base")
    difficulty: int = Field(..., ge=1, le=5)
    expected_time_min: int = Field(..., ge=1, le=180)
    max_points: float = Field(..., ge=0)


class RecommendRequest(BaseModel):
    goal: str = Field(..., pattern="^(maximize_points|maximize_learning)$")
    remaining_time_min: int = Field(..., ge=0, le=10000)
    tasks: List[TaskIn] = Field(..., min_length=1)


class RecommendResponse(BaseModel):
    recommended_task_id: str
    rationale: str
