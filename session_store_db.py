from uuid import uuid4
from sqlalchemy import select
from app.db import SessionLocal
from app.models.db_models import SessionRow
from app.models.session import SessionState


def _row_to_state(r: SessionRow) -> SessionState:
    return SessionState(
        session_id=r.session_id,
        goal=r.goal,
        remaining_time_min=r.remaining_time_min,
        skill_by_topic=r.skill_by_topic,
        last_recommended_task_id=r.last_recommended_task_id,
        recommendation_count=r.recommendation_count,
        choice_count=r.choice_count,
        choice_compliance=r.choice_compliance,
        time_compliance=r.time_compliance,
    )


def create_session(goal: str, remaining_time_min: int, skill_by_topic: dict) -> SessionState:
    session_id = str(uuid4())
    with SessionLocal() as db:
        row = SessionRow(
            session_id=session_id,
            goal=goal,
            remaining_time_min=remaining_time_min,
            skill_by_topic=skill_by_topic,
            last_recommended_task_id=None,
            recommendation_count=0,
            choice_count=0,
            choice_compliance=0.0,
            time_compliance=0.0,
        )
        db.add(row)
        db.commit()
        db.refresh(row)
        return _row_to_state(row)


def get_session(session_id: str) -> SessionState:
    with SessionLocal() as db:
        row = db.scalar(select(SessionRow).where(SessionRow.session_id == session_id))
        if not row:
            raise KeyError("session_not_found")
        return _row_to_state(row)


def update_session(state: SessionState) -> None:
    with SessionLocal() as db:
        row = db.scalar(select(SessionRow).where(SessionRow.session_id == state.session_id))
        if not row:
            raise KeyError("session_not_found")

        row.goal = state.goal
        row.remaining_time_min = state.remaining_time_min
        row.skill_by_topic = state.skill_by_topic
        row.last_recommended_task_id = state.last_recommended_task_id
        row.recommendation_count = state.recommendation_count
        row.choice_count = state.choice_count
        row.choice_compliance = float(state.choice_compliance)
        row.time_compliance = float(state.time_compliance)

        db.commit()
