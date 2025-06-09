from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# Include routers
app.include_router(auth_router)
app.include_router(repositories_router)


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


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Git Stats API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)