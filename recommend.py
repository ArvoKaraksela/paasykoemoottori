from fastapi import APIRouter
from app.engine.recommender import get_engine_status, recommend_task
from app.models.recommendation import RecommendRequest, RecommendResponse

router = APIRouter()

@router.get("/health")
def health():
    return get_engine_status()

@router.get("/")
def root():
    return {
        "name": "x-engine",
        "docs": "/docs",
        "health": "/health"
    }

@router.post("/recommend", response_model=RecommendResponse)
def recommend(payload: RecommendRequest):
    task_id, rationale = recommend_task(
        tasks=payload.tasks,
        goal=payload.goal,
        remaining_time_min=payload.remaining_time_min,
    )
    return RecommendResponse(recommended_task_id=task_id, rationale=rationale)
