#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
from datetime import date, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session

# Add the parent directory to sys.path to import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from git_utils import (
    validate_git_repository, get_commits_with_authors,
    get_commit_diff_stats, format_date_for_git, get_days_ago_date
)
from stats_parser import (
    parse_commit_diff_stats, create_author_stats_dict,
    add_author_commit_stats, finalize_author_stats
)

from ..core.models import Author, Repository, DailyAuthorStats


class WebGitAnalyzer:
    """Git analyzer adapted for web service with database storage."""
    
    def __init__(self, db: Session, repository: Repository):
        """
        Initialize the analyzer with database session and repository.
        
        Args:
            db: SQLAlchemy database session
            repository: Repository model instance
        """
        validate_git_repository(repository.local_path)
        self.db = db
        self.repository = repository
        self.repo_path = repository.local_path
    
    def get_or_create_author(self, email: str, name: str) -> Author:
        """Get existing author or create new one."""
        author = self.db.query(Author).filter(Author.email == email).first()
        
        if not author:
            author = Author(
                email=email,
                name=name,
                is_ai_coder=False  # Default to False, can be updated manually
            )
            self.db.add(author)
            self.db.flush()  # Get the ID
        
        return author
    
    def analyze_single_day(self, target_date: date) -> Dict[str, int]:
        """
        Analyze git statistics for a single day and store in database.
        
        Args:
            target_date: The date to analyze
            
        Returns:
            Dictionary with summary statistics for the day
        """
        try:
            since_datetime = format_date_for_git(target_date)
            until_datetime = format_date_for_git(target_date + timedelta(days=1))
            
            commits = get_commits_with_authors(self.repo_path, since_datetime, until_datetime)
            
            if not commits:
                return {
                    'commits_count': 0,
                    'added_lines': 0,
                    'deleted_lines': 0,
                    'total_files_changed': 0,
                    'authors_count': 0
                }
            
            author_stats = create_author_stats_dict()
            
            for commit in commits:
                # Get diff stats for this commit
                diff_output = get_commit_diff_stats(self.repo_path, commit['hash'])
                added, deleted, files = parse_commit_diff_stats(diff_output)
                
                add_author_commit_stats(
                    author_stats,
                    commit['author_email'],
                    commit['author_name'],
                    added,
                    deleted,
                    files
                )
            
            # Store in database
            total_added = 0
            total_deleted = 0
            total_files = 0
            authors_count = 0
            
            # Convert AuthorStats objects to final format first
            final_stats = finalize_author_stats(author_stats)
            
            for email, stats in final_stats.items():
                author = self.get_or_create_author(email, stats['name'])
                
                # Check if record already exists
                existing = self.db.query(DailyAuthorStats).filter(
                    DailyAuthorStats.repository_id == self.repository.id,
                    DailyAuthorStats.author_id == author.id,
                    DailyAuthorStats.date == target_date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.commits_count = stats['commits_count']
                    existing.added_lines = stats['added_lines']
                    existing.deleted_lines = stats['deleted_lines']
                    existing.files_changed = stats['total_files_changed']
                else:
                    # Create new record
                    daily_stat = DailyAuthorStats(
                        repository_id=self.repository.id,
                        author_id=author.id,
                        date=target_date,
                        commits_count=stats['commits_count'],
                        added_lines=stats['added_lines'],
                        deleted_lines=stats['deleted_lines'],
                        files_changed=stats['total_files_changed']
                    )
                    self.db.add(daily_stat)
                
                total_added += stats['added_lines']
                total_deleted += stats['deleted_lines']
                total_files += stats['total_files_changed']
                authors_count += 1
            
            self.db.commit()
            
            return {
                'commits_count': len(commits),
                'added_lines': total_added,
                'deleted_lines': total_deleted,
                'total_files_changed': total_files,
                'authors_count': authors_count
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Error analyzing day {target_date}: {e}")
            return None
    
    def analyze_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Analyze git statistics for a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of daily analysis results
        """
        results = []
        current_date = start_date
        
        while current_date <= end_date:
            result = self.analyze_single_day(current_date)
            results.append({
                'date': current_date,
                'stats': result
            })
            current_date += timedelta(days=1)
        
        # Update repository last analyzed timestamp
        from datetime import datetime, timezone
        self.repository.last_analyzed_at = datetime.now(timezone.utc)
        self.db.commit()
        
        return results
    
    def analyze_recent_days(self, days: int) -> List[Dict]:
        """
        Analyze recent N days.
        
        Args:
            days: Number of recent days to analyze
            
        Returns:
            List of daily analysis results
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)  # Include today
        
        return self.analyze_date_range(start_date, end_date)