from datetime import date, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, distinct
from ..core.models import Repository, DailyAuthorStats, Author, AnalysisJob, Commit, CommitCoAuthor
from ..schemas.statistics import (
    DailyStatsResponse, PeriodStatsResponse, AuthorStatsResponse,
    DailyBreakdownResponse, AuthorBreakdownResponse, RepoDailyResponse,
    DailyStatsWithAuthors, AuthorDailyContribution, DailyAuthorsBreakdownResponse,
    DailyAuthorStatsResponse, DailyAuthorDetail, AuthorDetail
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

    def get_repo_daily_stats(self, user_id: int, date_from: date, date_to: date, 
                           repo_id: Optional[int] = None, exclude_ai: bool = False) -> RepoDailyResponse:
        """Get daily stats with author breakdown for repositories."""
        
        # Build base query
        query = self.db.query(DailyAuthorStats).join(Repository).filter(
            Repository.user_id == user_id,
            DailyAuthorStats.date >= date_from,
            DailyAuthorStats.date <= date_to
        )
        
        # Filter by repository if specified
        repositories_included = []
        if repo_id:
            query = query.filter(DailyAuthorStats.repository_id == repo_id)
            repositories_included = [repo_id]
        else:
            # Get all user's repositories
            user_repos = self.db.query(Repository).filter(Repository.user_id == user_id).all()
            repositories_included = [repo.id for repo in user_repos]
        
        # Exclude AI coders if requested
        if exclude_ai:
            query = query.join(Author).filter(Author.is_ai_coder == False)
        
        # Execute query and group by date
        results = query.all()
        
        # Group results by date
        daily_data = {}
        for stat in results:
            stat_date = stat.date
            if stat_date not in daily_data:
                daily_data[stat_date] = []
            
            daily_data[stat_date].append(AuthorDailyContribution(
                author_id=stat.author_id,
                commits_count=stat.commits_count,
                added_lines=stat.added_lines,
                deleted_lines=stat.deleted_lines,
                files_changed=stat.files_changed
            ))
        
        # Create daily stats list
        daily_stats = []
        current_date = date_from
        while current_date <= date_to:
            authors_stats = daily_data.get(current_date, [])
            daily_stats.append(DailyStatsWithAuthors(
                date=current_date,
                daily_stats=authors_stats
            ))
            current_date += timedelta(days=1)
        
        return RepoDailyResponse(
            daily_stats=daily_stats,
            date_range=f"{date_from} to {date_to}",
            repositories_included=repositories_included
        )

    def get_daily_author_breakdown(self, repo_id: int, days: int, exclude_ai: bool = False) -> DailyAuthorsBreakdownResponse:
        """Get daily breakdown with full author details for multiple days."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Query to get daily author stats with full author details
        query = self.db.query(DailyAuthorStats, Author).join(Author).filter(
            and_(
                DailyAuthorStats.repository_id == repo_id,
                DailyAuthorStats.date >= start_date,
                DailyAuthorStats.date <= end_date
            )
        )
        
        # Exclude AI coders if requested
        if exclude_ai:
            query = query.filter(Author.is_ai_coder == False)
        
        # Order by date and author name for consistency
        query = query.order_by(DailyAuthorStats.date.desc(), Author.name)
        
        results = query.all()
        
        # Group results by date
        daily_data = {}
        for stat, author in results:
            stat_date = stat.date
            if stat_date not in daily_data:
                daily_data[stat_date] = []
            
            # Calculate derived values
            net_change = stat.added_lines - stat.deleted_lines
            total_activity = stat.added_lines + stat.deleted_lines
            
            daily_data[stat_date].append(DailyAuthorDetail(
                author=AuthorDetail(
                    id=author.id,
                    email=author.email,
                    name=author.name,
                    is_ai_coder=author.is_ai_coder
                ),
                commits_count=stat.commits_count,
                added_lines=stat.added_lines,
                deleted_lines=stat.deleted_lines,
                files_changed=stat.files_changed,
                net_change=net_change,
                total_activity=total_activity
            ))
        
        # Create daily stats list for the entire period
        daily_stats = []
        days_with_activity = 0
        
        current_date = start_date
        while current_date <= end_date:
            authors_data = daily_data.get(current_date, [])
            if authors_data:
                days_with_activity += 1
            
            daily_stats.append(DailyAuthorStatsResponse(
                date=current_date,
                authors=authors_data
            ))
            current_date += timedelta(days=1)
        
        return DailyAuthorsBreakdownResponse(
            daily_stats=daily_stats,
            period_days=days,
            total_days_with_activity=days_with_activity
        )
    
    def get_ai_coding_stats(self, repo_id: Optional[int] = None, user_id: Optional[int] = None, 
                           days: Optional[int] = None) -> Dict:
        """Get AI-powered coding statistics."""
        from sqlalchemy import case, exists
        
        # Build base query for commits
        query = self.db.query(Commit)
        
        if repo_id:
            query = query.filter(Commit.repository_id == repo_id)
        elif user_id:
            query = query.join(Repository).filter(Repository.user_id == user_id)
        
        # Apply date filter if specified
        if days:
            end_date = date.today()
            start_date = end_date - timedelta(days=days-1)
            query = query.filter(
                func.date(Commit.commit_datetime) >= start_date,
                func.date(Commit.commit_datetime) <= end_date
            )
        
        # Get total stats and AI-assisted stats
        total_result = query.with_entities(
            func.sum(Commit.added_lines + Commit.deleted_lines).label('total_lines'),
            func.count(Commit.id).label('total_commits')
        ).first()
        
        # Query for AI-assisted commits
        ai_subquery = self.db.query(CommitCoAuthor.commit_id).join(Author).filter(
            Author.is_ai_coder == True
        ).subquery()
        
        ai_result = query.filter(
            Commit.id.in_(self.db.query(ai_subquery.c.commit_id))
        ).with_entities(
            func.sum(Commit.added_lines + Commit.deleted_lines).label('ai_lines'),
            func.count(Commit.id).label('ai_commits')
        ).first()
        
        total_lines = total_result.total_lines or 0
        total_commits = total_result.total_commits or 0
        ai_lines = ai_result.ai_lines or 0
        ai_commits = ai_result.ai_commits or 0
        
        ai_lines_percentage = (ai_lines / total_lines * 100) if total_lines > 0 else 0
        ai_commits_percentage = (ai_commits / total_commits * 100) if total_commits > 0 else 0
        
        return {
            'total_lines': total_lines,
            'ai_assisted_lines': ai_lines,
            'ai_lines_percentage': round(ai_lines_percentage, 1),
            'total_commits': total_commits,
            'ai_assisted_commits': ai_commits,
            'ai_commits_percentage': round(ai_commits_percentage, 1)
        }
    
    def get_author_ai_stats(self, repo_id: int, days: int) -> List[Dict]:
        """Get AI assistance statistics per author."""
        from sqlalchemy import case
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Get all authors with their commit stats
        author_query = self.db.query(
            Author.id,
            Author.email,
            Author.name,
            Author.is_ai_coder,
            func.sum(Commit.added_lines + Commit.deleted_lines).label('total_lines'),
            func.count(Commit.id).label('total_commits')
        ).join(Commit).filter(
            Commit.repository_id == repo_id,
            func.date(Commit.commit_datetime) >= start_date,
            func.date(Commit.commit_datetime) <= end_date
        ).group_by(Author.id, Author.email, Author.name, Author.is_ai_coder)
        
        authors_stats = []
        
        for author_result in author_query.all():
            # Get AI-assisted stats for this author
            ai_subquery = self.db.query(CommitCoAuthor.commit_id).join(Author).filter(
                Author.is_ai_coder == True
            ).subquery()
            
            ai_result = self.db.query(
                func.sum(Commit.added_lines + Commit.deleted_lines).label('ai_lines'),
                func.count(Commit.id).label('ai_commits')
            ).filter(
                Commit.author_id == author_result.id,
                Commit.repository_id == repo_id,
                func.date(Commit.commit_datetime) >= start_date,
                func.date(Commit.commit_datetime) <= end_date,
                Commit.id.in_(self.db.query(ai_subquery.c.commit_id))
            ).first()
            
            total_lines = author_result.total_lines or 0
            total_commits = author_result.total_commits or 0
            ai_lines = ai_result.ai_lines or 0
            ai_commits = ai_result.ai_commits or 0
            
            ai_lines_percentage = (ai_lines / total_lines * 100) if total_lines > 0 else 0
            ai_commits_percentage = (ai_commits / total_commits * 100) if total_commits > 0 else 0
            
            authors_stats.append({
                'author_id': author_result.id,
                'author_email': author_result.email,
                'author_name': author_result.name,
                'is_ai_coder': author_result.is_ai_coder,
                'total_lines': total_lines,
                'ai_assisted_lines': ai_lines,
                'ai_lines_percentage': round(ai_lines_percentage, 1),
                'total_commits': total_commits,
                'ai_assisted_commits': ai_commits,
                'ai_commits_percentage': round(ai_commits_percentage, 1)
            })
        
        # Sort by total activity
        authors_stats.sort(key=lambda x: x['total_lines'], reverse=True)
        return authors_stats
    
    def get_ai_trends_over_time(self, repo_id: Optional[int] = None, user_id: Optional[int] = None, 
                               days: int = 30) -> List[Dict]:
        """Get AI assistance trends over time (daily breakdown)."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Build base query
        query = self.db.query(Commit)
        
        if repo_id:
            query = query.filter(Commit.repository_id == repo_id)
        elif user_id:
            query = query.join(Repository).filter(Repository.user_id == user_id)
        
        query = query.filter(
            func.date(Commit.commit_datetime) >= start_date,
            func.date(Commit.commit_datetime) <= end_date
        )
        
        # Get AI commit IDs
        ai_commit_ids = self.db.query(CommitCoAuthor.commit_id).join(Author).filter(
            Author.is_ai_coder == True
        ).all()
        ai_commit_ids_set = {row[0] for row in ai_commit_ids}
        
        # Group by date
        daily_trends = []
        current_date = start_date
        
        while current_date <= end_date:
            # Get commits for this day
            day_commits = query.filter(
                func.date(Commit.commit_datetime) == current_date
            ).all()
            
            total_lines = sum(commit.added_lines + commit.deleted_lines for commit in day_commits)
            total_commits = len(day_commits)
            
            ai_lines = sum(
                commit.added_lines + commit.deleted_lines 
                for commit in day_commits 
                if commit.id in ai_commit_ids_set
            )
            ai_commits = sum(1 for commit in day_commits if commit.id in ai_commit_ids_set)
            
            ai_lines_percentage = (ai_lines / total_lines * 100) if total_lines > 0 else 0
            
            daily_trends.append({
                'date': current_date.isoformat(),
                'total_lines': total_lines,
                'ai_assisted_lines': ai_lines,
                'ai_lines_percentage': round(ai_lines_percentage, 1),
                'total_commits': total_commits,
                'ai_assisted_commits': ai_commits
            })
            
            current_date += timedelta(days=1)
        
        return daily_trends