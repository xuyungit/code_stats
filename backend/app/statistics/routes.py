from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.models import User, Repository, AnalysisJob
from ..schemas.statistics import (
    DailyStatsResponse, PeriodStatsResponse, AuthorStatsResponse,
    DailyBreakdownResponse, AuthorBreakdownResponse,
    AnalysisJobRequest, AnalysisJobResponse, RepoDailyResponse
)
from ..auth.dependencies import get_current_user
from .services import StatisticsService
from .analyzer import WebGitAnalyzer

router = APIRouter(prefix="/repositories", tags=["statistics"])


def get_user_repository(repo_id: int, current_user: User, db: Session):
    """Helper to get repository and verify ownership."""
    repository = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id
    ).first()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    return repository


@router.get("/{repo_id}/stats/period", response_model=PeriodStatsResponse)
async def get_period_statistics(
    repo_id: int,
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    exclude_ai: bool = Query(default=False, description="Exclude AI coders from statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated statistics for a time period."""
    repository = get_user_repository(repo_id, current_user, db)
    
    stats_service = StatisticsService(db)
    
    # Check if we have data for this period
    if not stats_service.has_data_for_period(repo_id, days):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No statistics data found for the last {days} days. Please run analysis first."
        )
    
    return stats_service.get_period_stats(repo_id, days, exclude_ai)


@router.get("/{repo_id}/stats/daily", response_model=DailyBreakdownResponse)
async def get_daily_statistics(
    repo_id: int,
    days: int = Query(default=7, ge=1, le=90, description="Number of recent days to show"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily breakdown of statistics."""
    repository = get_user_repository(repo_id, current_user, db)
    
    stats_service = StatisticsService(db)
    
    # Check if we have data for this period
    if not stats_service.has_data_for_period(repo_id, days):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No statistics data found for the last {days} days. Please run analysis first."
        )
    
    return stats_service.get_daily_breakdown(repo_id, days)


@router.get("/{repo_id}/stats/authors", response_model=AuthorBreakdownResponse)
async def get_author_statistics(
    repo_id: int,
    days: int = Query(default=7, ge=1, le=365, description="Number of days to analyze"),
    exclude_ai: bool = Query(default=False, description="Exclude AI coders from statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get author breakdown of statistics."""
    repository = get_user_repository(repo_id, current_user, db)
    
    stats_service = StatisticsService(db)
    
    # Check if we have data for this period
    if not stats_service.has_data_for_period(repo_id, days):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No statistics data found for the last {days} days. Please run analysis first."
        )
    
    return stats_service.get_author_stats(repo_id, days, exclude_ai)


@router.post("/{repo_id}/analyze", response_model=AnalysisJobResponse)
async def trigger_analysis(
    repo_id: int,
    request: AnalysisJobRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Trigger git analysis for a repository."""
    repository = get_user_repository(repo_id, current_user, db)
    
    # Create analysis job
    job = AnalysisJob(
        repository_id=repo_id,
        status="pending",
        job_type="manual_analysis",
        date_from=date.today() - timedelta(days=request.days),
        date_to=date.today()
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    try:
        # Update job status to running
        job.status = "running"
        job.started_at = datetime.now()
        db.commit()
        
        # Run analysis
        analyzer = WebGitAnalyzer(db, repository)
        results = analyzer.analyze_recent_days(request.days)
        
        # Update job status to completed
        job.status = "completed"
        job.completed_at = datetime.now()
        job.records_processed = len(results)
        db.commit()
        
        return AnalysisJobResponse(
            id=job.id,
            status=job.status,
            job_type=job.job_type,
            date_from=job.date_from,
            date_to=job.date_to,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error_message=job.error_message,
            records_processed=job.records_processed,
            created_at=job.created_at
        )
        
    except Exception as e:
        # Update job status to failed
        job.status = "failed"
        job.completed_at = datetime.now()
        job.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{repo_id}/jobs", response_model=list[AnalysisJobResponse])
async def list_analysis_jobs(
    repo_id: int,
    limit: int = Query(default=10, ge=1, le=100, description="Number of jobs to return"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List analysis jobs for a repository."""
    repository = get_user_repository(repo_id, current_user, db)
    
    jobs = db.query(AnalysisJob).filter(
        AnalysisJob.repository_id == repo_id
    ).order_by(AnalysisJob.created_at.desc()).limit(limit).all()
    
    return [AnalysisJobResponse(
        id=job.id,
        status=job.status,
        job_type=job.job_type,
        date_from=job.date_from,
        date_to=job.date_to,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        records_processed=job.records_processed,
        created_at=job.created_at
    ) for job in jobs]


@router.get("/{repo_id}/jobs/{job_id}", response_model=AnalysisJobResponse)
async def get_analysis_job(
    repo_id: int,
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific analysis job."""
    repository = get_user_repository(repo_id, current_user, db)
    
    job = db.query(AnalysisJob).filter(
        AnalysisJob.id == job_id,
        AnalysisJob.repository_id == repo_id
    ).first()
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis job not found"
        )
    
    return AnalysisJobResponse(
        id=job.id,
        status=job.status,
        job_type=job.job_type,
        date_from=job.date_from,
        date_to=job.date_to,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error_message=job.error_message,
        records_processed=job.records_processed,
        created_at=job.created_at
    )


# Create a new router for general statistics (not tied to specific repository)
stats_router = APIRouter(prefix="/stats", tags=["cross-repo-statistics"])


@stats_router.get("/repo-daily", response_model=RepoDailyResponse)
async def get_repo_daily_stats(
    date_from: date = Query(description="Start date (YYYY-MM-DD)"),
    date_to: date = Query(description="End date (YYYY-MM-DD)"),
    repo: str = Query(description="Repository ID or 'all' for all repositories"),
    exclude_ai: bool = Query(default=False, description="Exclude AI coders from statistics"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily statistics with author breakdown for repositories."""
    
    # Validate date range
    if date_to < date_from:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date"
        )
    
    # Parse repository parameter
    repo_id = None
    if repo != "all":
        try:
            repo_id = int(repo)
            # Verify user owns this repository
            repository = db.query(Repository).filter(
                Repository.id == repo_id,
                Repository.user_id == current_user.id
            ).first()
            if not repository:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Repository not found"
                )
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Repository parameter must be 'all' or a valid repository ID"
            )
    
    stats_service = StatisticsService(db)
    return stats_service.get_repo_daily_stats(
        user_id=current_user.id,
        date_from=date_from,
        date_to=date_to,
        repo_id=repo_id,
        exclude_ai=exclude_ai
    )