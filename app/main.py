from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth

app = FastAPI(
    title=settings.APP_NAME,
    description="SafeHer Women Safety Platform Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS origins for your frontend
CORS_ORIGINS = [
    "http://localhost:3000",   # Your React frontend
    "http://localhost:5173",   # Vite default
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth router (no reports yet)
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "service": settings.APP_NAME}