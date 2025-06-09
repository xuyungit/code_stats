from datetime import date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, distinct
from ..core.models import Repository, DailyAuthorStats, Author, AnalysisJob
from ..schemas.statistics import (
    DailyStatsResponse, PeriodStatsResponse, AuthorStatsResponse,
    DailyBreakdownResponse, AuthorBreakdownResponse
)


class StatisticsService:
    """Service for querying statistics from the database."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_daily_stats(self, repo_id: int, target_date: date) -> Optional[DailyStatsResponse]:
        """Get aggregated daily stats for a repository on a specific date."""
        # Query to aggregate all authors' stats for the day
        result = self.db.query(
            func.coalesce(func.sum(DailyAuthorStats.commits_count), 0).label('commits_count'),
            func.coalesce(func.sum(DailyAuthorStats.added_lines), 0).label('added_lines'),
            func.coalesce(func.sum(DailyAuthorStats.deleted_lines), 0).label('deleted_lines'),
            func.coalesce(func.sum(DailyAuthorStats.files_changed), 0).label('files_changed'),
            func.count(distinct(DailyAuthorStats.author_id)).label('authors_count')
        ).filter(
            and_(
                DailyAuthorStats.repository_id == repo_id,
                DailyAuthorStats.date == target_date
            )
        ).first()
        
        if not result or result.commits_count == 0:
            return DailyStatsResponse(
                date=target_date,
                commits_count=0,
                added_lines=0,
                deleted_lines=0,
                files_changed=0,
                net_change=0,
                total_activity=0,
                authors_count=0
            )
        
        net_change = result.added_lines - result.deleted_lines
        total_activity = result.added_lines + result.deleted_lines
        
        return DailyStatsResponse(
            date=target_date,
            commits_count=result.commits_count,
            added_lines=result.added_lines,
            deleted_lines=result.deleted_lines,
            files_changed=result.files_changed,
            net_change=net_change,
            total_activity=total_activity,
            authors_count=result.authors_count
        )
    
    def get_period_stats(self, repo_id: int, days: int, exclude_ai: bool = False) -> PeriodStatsResponse:
        """Get aggregated stats for a period."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Base query
        query = self.db.query(
            func.coalesce(func.sum(DailyAuthorStats.commits_count), 0).label('commits_count'),
            func.coalesce(func.sum(DailyAuthorStats.added_lines), 0).label('added_lines'),
            func.coalesce(func.sum(DailyAuthorStats.deleted_lines), 0).label('deleted_lines'),
            func.coalesce(func.sum(DailyAuthorStats.files_changed), 0).label('files_changed'),
            func.count(distinct(DailyAuthorStats.author_id)).label('authors_count')
        ).filter(
            and_(
                DailyAuthorStats.repository_id == repo_id,
                DailyAuthorStats.date >= start_date,
                DailyAuthorStats.date <= end_date
            )
        )
        
        # Exclude AI coders if requested
        if exclude_ai:
            query = query.join(Author).filter(Author.is_ai_coder == False)
        
        result = query.first()
        
        if not result:
            result = type('obj', (object,), {
                'commits_count': 0, 'added_lines': 0, 'deleted_lines': 0,
                'files_changed': 0, 'authors_count': 0
            })()
        
        net_change = result.added_lines - result.deleted_lines
        total_activity = result.added_lines + result.deleted_lines
        
        return PeriodStatsResponse(
            period_days=days,
            start_date=start_date,
            end_date=end_date,
            commits_count=result.commits_count,
            added_lines=result.added_lines,
            deleted_lines=result.deleted_lines,
            files_changed=result.files_changed,
            net_change=net_change,
            total_activity=total_activity,
            authors_count=result.authors_count
        )
    
    def get_daily_breakdown(self, repo_id: int, days: int) -> DailyBreakdownResponse:
        """Get daily breakdown for multiple days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        daily_stats = []
        days_with_activity = 0
        
        current_date = start_date
        while current_date <= end_date:
            day_stats = self.get_daily_stats(repo_id, current_date)
            if day_stats.commits_count > 0:
                days_with_activity += 1
            daily_stats.append(day_stats)
            current_date += timedelta(days=1)
        
        return DailyBreakdownResponse(
            daily_stats=daily_stats,
            period_days=days,
            total_days_with_activity=days_with_activity
        )
    
    def get_author_stats(self, repo_id: int, days: int, exclude_ai: bool = False) -> AuthorBreakdownResponse:
        """Get author breakdown for a period."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Query to get author stats
        query = self.db.query(
            Author.email,
            Author.name,
            Author.is_ai_coder,
            func.sum(DailyAuthorStats.commits_count).label('commits_count'),
            func.sum(DailyAuthorStats.added_lines).label('added_lines'),
            func.sum(DailyAuthorStats.deleted_lines).label('deleted_lines'),
            func.sum(DailyAuthorStats.files_changed).label('files_changed')
        ).join(Author).filter(
            and_(
                DailyAuthorStats.repository_id == repo_id,
                DailyAuthorStats.date >= start_date,
                DailyAuthorStats.date <= end_date
            )
        ).group_by(
            Author.email, Author.name, Author.is_ai_coder
        )
        
        # Exclude AI coders if requested
        if exclude_ai:
            query = query.filter(Author.is_ai_coder == False)
        
        # Order by total activity
        query = query.order_by(
            (func.sum(DailyAuthorStats.added_lines) + func.sum(DailyAuthorStats.deleted_lines)).desc()
        )
        
        results = query.all()
        
        authors = []
        for result in results:
            net_change = result.added_lines - result.deleted_lines
            total_activity = result.added_lines + result.deleted_lines
            
            authors.append(AuthorStatsResponse(
                author_email=result.email,
                author_name=result.name,
                is_ai_coder=result.is_ai_coder,
                commits_count=result.commits_count,
                added_lines=result.added_lines,
                deleted_lines=result.deleted_lines,
                files_changed=result.files_changed,
                net_change=net_change,
                total_activity=total_activity
            ))
        
        return AuthorBreakdownResponse(
            authors=authors,
            period_days=days,
            total_authors=len(authors)
        )
    
    def get_repository_last_analysis(self, repo_id: int) -> Optional[AnalysisJob]:
        """Get the last analysis job for a repository."""
        return self.db.query(AnalysisJob).filter(
            AnalysisJob.repository_id == repo_id
        ).order_by(AnalysisJob.created_at.desc()).first()
    
    def has_data_for_period(self, repo_id: int, days: int) -> bool:
        """Check if repository has any data for the specified period."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        count = self.db.query(DailyAuthorStats).filter(
            and_(
                DailyAuthorStats.repository_id == repo_id,
                DailyAuthorStats.date >= start_date,
                DailyAuthorStats.date <= end_date
            )
        ).count()
        
        return count > 0