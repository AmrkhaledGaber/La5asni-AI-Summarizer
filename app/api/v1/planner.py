from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Data Models
class TrainingModule(BaseModel):
    title: str
    description: Optional[str] = None  # Added description field
    estimated_minutes: int

class PlanRequest(BaseModel):
    training_modules: List[TrainingModule]
    plan_mode: str  # "auto" or "manual"
    num_days: Optional[int] = None
    hours_per_day: Optional[int] = None  # Changed to match frontend

@router.post("/plan/")
def generate_plan(request: PlanRequest):
    modules = request.training_modules

    if not modules:
        raise HTTPException(status_code=400, detail="No training modules provided.")

    total_minutes = sum(module.estimated_minutes for module in modules)

    # Auto mode calculation
    if request.plan_mode == "auto":
        hours_per_day = 4  # default
        minutes_per_day = hours_per_day * 60
        num_days = max(1, (total_minutes + minutes_per_day - 1) // minutes_per_day)
    else:
        if not request.num_days or not request.hours_per_day:
            raise HTTPException(status_code=400, detail="Specify num_days and daily_hours in manual mode.")
        num_days = request.num_days
        minutes_per_day = request.hours_per_day * 60

    # Distribute modules across days
    plan = []
    day = 1
    current_day_minutes = 0
    current_day_modules = []

    for module in modules:
        if current_day_minutes + module.estimated_minutes <= minutes_per_day:
            current_day_modules.append(module)
            current_day_minutes += module.estimated_minutes
        else:
            # Append current day
            plan.append({
                "day": day,
                "total_minutes": current_day_minutes,
                "sessions": [
                    {"title": m.title, "description": m.description, "duration": m.estimated_minutes} for m in current_day_modules
                ]
            })
            day += 1
            current_day_modules = [module]
            current_day_minutes = module.estimated_minutes

    # Add remaining modules
    if current_day_modules:
        plan.append({
            "day": day,
            "total_minutes": current_day_minutes,
            "sessions": [
                {"title": m.title, "description": m.description, "duration": m.estimated_minutes} for m in current_day_modules
            ]
        })

    return {"plan": plan}
