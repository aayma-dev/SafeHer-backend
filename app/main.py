from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import auth, reports

app = FastAPI(
    title=settings.APP_NAME,
    description="SafeHer Women Safety Platform Backend API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS origins for Vercel deployment
CORS_ORIGINS = [
    # Local development
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:5173",
    # Vercel production
    "https://safeher-frontend.vercel.app",
    "https://*.vercel.app",
]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(reports.router)

@app.get("/")
def root():
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}