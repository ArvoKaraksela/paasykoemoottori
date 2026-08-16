from typing import Dict
from uuid import uuid4
from app.models.session import SessionState


# In-memory store (MVP). Later replaced by DB.
_SESSIONS: Dict[str, SessionState] = {}


def create_session(goal: str, remaining_time_min: int, skill_by_topic: Dict[str, float]) -> SessionState:
    session_id = str(uuid4())
    state = SessionState(
        session_id=session_id,
        goal=goal,
        remaining_time_min=remaining_time_min,
        skill_by_topic=skill_by_topic,
    )
    _SESSIONS[session_id] = state
    return state


def get_session(session_id: str) -> SessionState:
    if session_id not in _SESSIONS:
        raise KeyError("session_not_found")
    return _SESSIONS[session_id]


def update_session(state: SessionState) -> None:
    _SESSIONS[state.session_id] = state
