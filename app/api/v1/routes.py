from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.services.parser import extract_text
from app.services.analyzer import analyze_document
from app.models.schemas import AnalysisResponse
from app.services.database import save_analysis
from datetime import datetime
import json
router = APIRouter()

@router.post("/analyze/", response_model=AnalysisResponse)
async def analyze(
    file: UploadFile = File(...),
    provider: str = Form("groq")  # استقبل provider من الـ frontend (default = groq)
):
    content = await file.read()
    parsed = extract_text(file.filename, content)

    # Call analyzer with required arguments
    result = analyze_document(
        parsed["text"],
        parsed["num_pages"],
        parsed["useful_ratio"],
        provider=provider  # Use the provider from the frontend
    )

    return result

@router.post("/refine/")
async def refine_summary(request: dict):
    from app.services.refiner import refine_content
    text = request.get("text")
    user_note = request.get("user_feedback")

    if not text or not user_note:
        raise HTTPException(status_code=400, detail="Missing required fields.")

    refined = refine_content(text, user_note)
    return refined


