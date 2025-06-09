from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
import os
from .core.config import settings
from .core.migration_manager import migration_manager
from .auth.routes import router as auth_router
from .repositories.routes import router as repositories_router

# Create FastAPI app
app = FastAPI(
    title="Git Stats API",
    description="API for analyzing git repository statistics",
    version="1.0.0",
    debug=settings.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files from Vue build FIRST
frontend_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    # Mount assets directory for JS/CSS files
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

# Include routers with API prefix AFTER static mounts
app.include_router(auth_router, prefix="/api")
app.include_router(repositories_router, prefix="/api")

# Import statistics router after other imports to avoid circular dependencies
from .statistics.routes import router as statistics_router
app.include_router(statistics_router, prefix="/api")

# API routes defined
@app.get("/api/")
async def root():
    """Root endpoint."""
    return {"message": "Git Stats API", "version": "1.0.0"}

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Frontend routes (after API routes)
if frontend_dir.exists():
    # Serve favicon
    @app.get("/favicon.ico")
    async def favicon():
        favicon_path = frontend_dir / "favicon.ico"
        if favicon_path.exists():
            return FileResponse(str(favicon_path))
        return {"error": "Favicon not found"}
    
    # Catch-all route for Vue SPA (must be absolute last)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve Vue frontend for all non-API routes."""
        # For any non-API route, serve index.html (SPA routing)
        index_file = frontend_dir / "index.html"
        return FileResponse(str(index_file))


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("Starting up Git Stats API...")
    
    # Run migrations
    try:
        migration_manager.migrate_up()
        print("Database migrations completed successfully")
    except Exception as e:
        print(f"Migration failed: {e}")
        raise




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)