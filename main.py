"""
VendorGuard - FastAPI Application Entry Point
Serves the API backend and static React frontend.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.models import HealthResponse
from config import config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    missing_keys = config.validate()
    if missing_keys:
        print(f"⚠️  Warning: Missing API keys: {', '.join(missing_keys)}")
        print("   Some features may not work. Set them in .env file.")
    else:
        print("✅ All API keys configured")

    print(f"🚀 VendorGuard starting on {config.HOST}:{config.PORT}")
    print(f"   Risk threshold: {config.RISK_THRESHOLD}")
    print(f"   Scan timeout: {config.SCAN_TIMEOUT_SECONDS}s")

    yield

    # Shutdown
    print("👋 VendorGuard shutting down")


# Create FastAPI app
app = FastAPI(
    title="VendorGuard API",
    description="AI-Powered Supply Chain Risk Agent for SME Manufacturers",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware (allow frontend dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================
# API Routes
# ============================================

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint. Returns service status and version."""
    return HealthResponse(status="ok", version="1.0")


# TODO (Phase 4): Add scan, vendor, and alert endpoints
# from api.routes import router as api_router
# app.include_router(api_router, prefix="/api")


# ============================================
# Static Frontend (Production)
# ============================================

# Mount static files if the build directory exists
static_dir = config.STATIC_FILES_PATH
if os.path.isdir(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
    print(f"📦 Serving frontend from {static_dir}")


# ============================================
# CLI Entry Point
# ============================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=config.DEBUG,
    )
