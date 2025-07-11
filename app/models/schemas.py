from pydantic import BaseModel
from typing import List

class TrainingModule(BaseModel):
    title: str
    description: str
    estimated_minutes: int

class AnalysisResponse(BaseModel):
    summary: str
    key_points: List[str]
    training_modules: List[TrainingModule]  # <-- هنا التعديل الأساسي
    num_pages: int
    useful_text_ratio: float
    num_key_points: int
