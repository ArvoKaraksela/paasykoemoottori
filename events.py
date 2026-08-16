from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime


EventType = Literal["recommendation", "choice"]


class EventOut(BaseModel):
    id: str
    session_id: str
    event_type: EventType
    created_at: datetime

    # Common fields
    payload: Dict[str, Any] = Field(default_factory=dict)

    # Convenience (optional)
    recommended_task_id: Optional[str] = None
    chosen_task_id: Optional[str] = None
    time_spent_min: Optional[int] = None
    choice_compliance_after: Optional[float] = None
    time_compliance_after: Optional[float] = None