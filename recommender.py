from typing import List
from app.models.recommendation import TaskIn


def get_engine_status():
    """
    Core engine health check.
    This function exists to separate API layer from engine layer.
    """
    return {"engine": "x-engine core", "status": "operational"}


def recommend_task(tasks: List[TaskIn], goal: str, remaining_time_min: int):
    """
    v1 heuristic:
    - Filter tasks that fit in remaining time
    - Score by (max_points / expected_time_min)
    - Slight bonus for easier tasks when goal is maximize_points (higher success probability proxy)
    """
    feasible = [t for t in tasks if t.expected_time_min <= remaining_time_min]

    if not feasible:
        # If nothing fits, pick the shortest task as a fallback.
        best = min(tasks, key=lambda t: t.expected_time_min)
        return best.id, "No task fits remaining time; picked shortest as fallback."

    def score(t: TaskIn) -> float:
        base = float(t.max_points) / max(1, int(t.expected_time_min))
        if goal == "maximize_points":
            # Easier tasks are more likely to be solved -> small bonus
            base += (5 - t.difficulty) * 0.02
        else:
            # Learning mode: prefer medium difficulty
            base += (1.0 - abs(t.difficulty - 3) * 0.15)
        return base

    best = max(feasible, key=score)

    rationale = (
        f"Picked by best points-per-minute within remaining time. "
        f"topic={best.topic}, difficulty={best.difficulty}, "
        f"time={best.expected_time_min}min, points={best.max_points}."
    )
    return best.id, rationale
