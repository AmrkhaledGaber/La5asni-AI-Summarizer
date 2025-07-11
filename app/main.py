from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes import router as core_router
from app.api.v1 import planner
from app.services.database import init_db

app = FastAPI(
    title="La5asni - Document Analyzer",
    description="Summarize, Extract, and Generate Training Modules from Documents.",
    version="1.0.0",
)

# ✅ تهيئة قاعدة البيانات (لو فيه حاجة مستقبلًا)
init_db()

# ✅ دعم CORS علشان الفرونت يشتغل بدون مشاكل
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ممكن تغيّرها للدومين النهائي
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ربط الـ routers
app.include_router(core_router, prefix="/api/v1")
app.include_router(planner.router, prefix="/api/v1")

# ✅ Root endpoint
@app.get("/")
def root():
    return {"message": "Welcome to La5asni - Document Analyzer API"}
