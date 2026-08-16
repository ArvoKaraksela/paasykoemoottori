from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    pass


class SessionRow(Base):
    __tablename__ = "sessions"

    session_id: Mapped[str] = mapped_column(String, primary_key=True)

    goal: Mapped[str] = mapped_column(String)
    remaining_time_min: Mapped[int] = mapped_column(Integer)
    skill_by_topic: Mapped[dict] = mapped_column(JSONB)

    last_recommended_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
    recommendation_count: Mapped[int] = mapped_column(Integer, default=0)

    choice_count: Mapped[int] = mapped_column(Integer, default=0)
    choice_compliance: Mapped[float] = mapped_column(Float, default=0.0)
    time_compliance: Mapped[float] = mapped_column(Float, default=0.0)


class SessionEventRow(Base):
    __tablename__ = "session_events"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String, index=True)

    event_type: Mapped[str] = mapped_column(String)  # "recommendation" | "choice"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    recommended_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
    chosen_task_id: Mapped[str | None] = mapped_column(String, nullable=True)
    time_spent_min: Mapped[int | None] = mapped_column(Integer, nullable=True)

    choice_compliance_after: Mapped[float | None] = mapped_column(Float, nullable=True)
    time_compliance_after: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Research snapshot of inputs/outputs
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)


# Helpful index if you later query events by session + time
Index("ix_session_events_session_time", SessionEventRow.session_id, SessionEventRow.created_at)