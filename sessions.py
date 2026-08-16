from fastapi import APIRouter, HTTPException

from app.db import SessionLocal
from app.engine.recommender import recommend_task
from app.engine.session_store_db import create_session, get_session, update_session
from app.models.db_models import SessionEventRow
from app.models.session import (
    ChoiceRequest,
    CreateSessionRequest,
    CreateSessionResponse,
    SessionRecommendRequest,
    SessionState,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=CreateSessionResponse)
def create_session_endpoint(payload: CreateSessionRequest):
    state = create_session(
        goal=payload.goal,
        remaining_time_min=payload.remaining_time_min,
        skill_by_topic=payload.skill_by_topic,
    )
    return CreateSessionResponse(session_id=state.session_id)


@router.get("/{session_id}", response_model=SessionState)
def get_session_endpoint(session_id: str):
    try:
        return get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")


@router.post("/{session_id}/recommend")
def recommend_in_session(session_id: str, payload: SessionRecommendRequest):
    """
    MVP: client sends tasks for now.
    Later: tasks come from DB by exam/collection id.
    """
    tasks = payload.tasks

    try:
        state = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")

    task_id, rationale = recommend_task(
        tasks=tasks,
        goal=state.goal,
        remaining_time_min=state.remaining_time_min,
    )

    # Update session state
    state.last_recommended_task_id = task_id
    state.recommendation_count += 1
    update_session(state)

    # --- Log recommendation event ---
    with SessionLocal() as db:
        event = SessionEventRow(
            session_id=session_id,
            event_type="recommendation",
            recommended_task_id=task_id,
            choice_compliance_after=float(state.choice_compliance),
            time_compliance_after=float(state.time_compliance),
            payload={
                "remaining_time_min": state.remaining_time_min,
                "recommendation_count": state.recommendation_count,
                "tasks": [t.model_dump() for t in tasks],
                "recommended_task_id": task_id,
                "rationale": rationale,
            },
        )
        db.add(event)
        db.commit()

    return {"recommended_task_id": task_id, "rationale": rationale}


@router.post("/{session_id}/choice", response_model=SessionState)
def record_choice(session_id: str, payload: ChoiceRequest):
    """
    Records what the user chose and how much time they spent.
    Updates compliance metrics.
    """
    try:
        state = get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="session_not_found")

    # Update counts
    state.choice_count += 1

    # Choice compliance: did user follow last recommendation?
    followed = None
    if state.last_recommended_task_id is not None:
        followed = (payload.chosen_task_id == state.last_recommended_task_id)
        # running average
        prev = state.choice_compliance
        n = state.choice_count
        state.choice_compliance = ((prev * (n - 1)) + (1.0 if followed else 0.0)) / n

    # Time compliance: did user stay within recommended budget?
    # MVP rule: "compliant" if they used <= 25% of remaining time (placeholder until we track per-task budgets)
    time_ok = payload.time_spent_min <= max(1, int(state.remaining_time_min * 0.25))
    prev_t = state.time_compliance
    n = state.choice_count
    state.time_compliance = ((prev_t * (n - 1)) + (1.0 if time_ok else 0.0)) / n

    # Update remaining time
    before_time = state.remaining_time_min
    state.remaining_time_min = max(0, state.remaining_time_min - payload.time_spent_min)

    update_session(state)

    # --- Log choice event ---
    with SessionLocal() as db:
        event = SessionEventRow(
            session_id=session_id,
            event_type="choice",
            chosen_task_id=payload.chosen_task_id,
            time_spent_min=payload.time_spent_min,
            recommended_task_id=state.last_recommended_task_id,
            choice_compliance_after=float(state.choice_compliance),
            time_compliance_after=float(state.time_compliance),
            payload={
                "chosen_task_id": payload.chosen_task_id,
                "time_spent_min": payload.time_spent_min,
                "followed_recommendation": followed,
                "time_ok": time_ok,
                "remaining_time_before": before_time,
                "remaining_time_after": state.remaining_time_min,
                "choice_count": state.choice_count,
            },
        )
        db.add(event)
        db.commit()

    return state