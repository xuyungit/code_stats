from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List


class DailyStatsResponse(BaseModel):
    date: date
    commits_count: int
    added_lines: int
    deleted_lines: int
    files_changed: int
    net_change: int
    total_activity: int
    authors_count: int
    
    class Config:
        from_attributes = True


class PeriodStatsResponse(BaseModel):
    period_days: int
    start_date: date
    end_date: date
    commits_count: int
    added_lines: int
    deleted_lines: int
    files_changed: int
    net_change: int
    total_activity: int
    authors_count: int
    
    class Config:
        from_attributes = True


class AuthorStatsResponse(BaseModel):
    author_email: str
    author_name: str
    is_ai_coder: bool
    commits_count: int
    added_lines: int
    deleted_lines: int
    files_changed: int
    net_change: int
    total_activity: int
    
    class Config:
        from_attributes = True


class DailyBreakdownResponse(BaseModel):
    daily_stats: List[DailyStatsResponse]
    period_days: int
    total_days_with_activity: int
    
    class Config:
        from_attributes = True


class AuthorBreakdownResponse(BaseModel):
    authors: List[AuthorStatsResponse]
    period_days: int
    total_authors: int
    
    class Config:
        from_attributes = True


class AuthorDailyContribution(BaseModel):
    author_id: int
    commits_count: int
    added_lines: int
    deleted_lines: int
    files_changed: int
    
    class Config:
        from_attributes = True


class DailyStatsWithAuthors(BaseModel):
    date: date
    daily_stats: List[AuthorDailyContribution]
    
    class Config:
        from_attributes = True


class RepoDailyResponse(BaseModel):
    daily_stats: List[DailyStatsWithAuthors]
    date_range: str
    repositories_included: List[int]
    
    class Config:
        from_attributes = True


class AnalysisJobRequest(BaseModel):
    days: Optional[int] = 30
    force_refresh: Optional[bool] = False


class AnalysisJobResponse(BaseModel):
    id: int
    status: str
    job_type: str
    date_from: Optional[date]
    date_to: Optional[date]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    records_processed: int
    created_at: datetime
    
    class Config:
        from_attributes = True