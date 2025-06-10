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
    validate_git_repository, get_commits_with_authors, get_commits_detailed,
    get_commit_diff_stats, format_date_for_git, get_days_ago_date
)
from stats_parser import (
    parse_commit_diff_stats, create_author_stats_dict,
    add_author_commit_stats, finalize_author_stats
)

from ..core.models import Author, Repository, DailyAuthorStats, Commit, CommitCoAuthor


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
    
    def get_or_create_author(self, email: str, name: str, is_ai: bool = False) -> Author:
        """Get existing author or create new one."""
        author = self.db.query(Author).filter(Author.email == email).first()
        
        if not author:
            author = Author(
                email=email,
                name=name,
                is_ai_coder=is_ai
            )
            self.db.add(author)
            self.db.flush()  # Get the ID
        
        return author
    
    def detect_co_authors(self, message: str) -> List[str]:
        """Detect co-authors from commit message."""
        co_authors = []
        lines = message.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('Co-Authored-By:'):
                # Extract author info from "Co-Authored-By: Name <email>" or "Co-Authored-By: Claude"
                co_author_part = line[15:].strip()  # Remove "Co-Authored-By:"
                
                if co_author_part == "Claude":
                    # Special handling for Claude AI
                    co_authors.append({
                        'name': 'Claude',
                        'email': 'claude@anthropic.com',
                        'is_ai': True
                    })
                elif '<' in co_author_part and '>' in co_author_part:
                    # Standard format: "Name <email>"
                    name_part = co_author_part.split('<')[0].strip()
                    email_match = co_author_part.split('<')[1].split('>')[0].strip()
                    # Check if this is Claude with different email format
                    is_claude_ai = name_part.lower() == 'claude' or 'claude' in email_match.lower()
                    co_authors.append({
                        'name': name_part,
                        'email': email_match,
                        'is_ai': is_claude_ai
                    })
        
        return co_authors
    
    def analyze_single_day(self, target_date: date) -> Dict[str, int]:
        """
        Analyze git statistics for a single day and store individual commits in database.
        
        Args:
            target_date: The date to analyze
            
        Returns:
            Dictionary with summary statistics for the day
        """
        try:
            since_datetime = format_date_for_git(target_date)
            until_datetime = format_date_for_git(target_date + timedelta(days=1))
            
            commits = get_commits_detailed(self.repo_path, since_datetime, until_datetime)
            
            if not commits:
                return {
                    'commits_count': 0,
                    'added_lines': 0,
                    'deleted_lines': 0,
                    'total_files_changed': 0,
                    'authors_count': 0
                }
            
            stored_commits = 0
            total_added = 0
            total_deleted = 0
            total_files = 0
            unique_authors = set()
            
            for commit_info in commits:
                # Check if commit already exists
                existing_commit = self.db.query(Commit).filter(
                    Commit.repository_id == self.repository.id,
                    Commit.hash == commit_info['hash']
                ).first()
                
                if existing_commit:
                    continue  # Skip already processed commits
                
                # Get diff stats for this commit
                diff_output = get_commit_diff_stats(self.repo_path, commit_info['hash'])
                added, deleted, files_set = parse_commit_diff_stats(diff_output)
                files_count = len(files_set)  # Convert set to count
                
                # Parse commit datetime
                from datetime import datetime
                commit_dt = datetime.fromisoformat(commit_info['datetime'].replace('Z', '+00:00'))
                
                # Create or get primary author
                primary_author = self.get_or_create_author(
                    commit_info['author_email'], 
                    commit_info['author_name']
                )
                
                # Store the commit
                commit_record = Commit(
                    repository_id=self.repository.id,
                    author_id=primary_author.id,
                    hash=commit_info['hash'],
                    message=commit_info['message'],
                    commit_datetime=commit_dt,
                    added_lines=added,
                    deleted_lines=deleted,
                    files_changed=files_count
                )
                self.db.add(commit_record)
                self.db.flush()  # Get the commit ID
                
                # Detect and store co-authors
                co_authors = self.detect_co_authors(commit_info['message'])
                for co_author_info in co_authors:
                    co_author = self.get_or_create_author(
                        co_author_info['email'],
                        co_author_info['name'],
                        co_author_info['is_ai']
                    )
                    
                    # Create co-author relationship
                    co_author_record = CommitCoAuthor(
                        commit_id=commit_record.id,
                        author_id=co_author.id
                    )
                    self.db.add(co_author_record)
                
                stored_commits += 1
                total_added += added
                total_deleted += deleted
                total_files += files_count
                unique_authors.add(primary_author.id)
                
                # Add co-authors to unique authors count
                for co_author_info in co_authors:
                    co_author = self.get_or_create_author(
                        co_author_info['email'],
                        co_author_info['name'],
                        co_author_info['is_ai']
                    )
                    unique_authors.add(co_author.id)
            
            # Now calculate and store daily stats from commits
            self._calculate_daily_stats_from_commits(target_date)
            
            self.db.commit()
            
            return {
                'commits_count': stored_commits,
                'added_lines': total_added,
                'deleted_lines': total_deleted,
                'total_files_changed': total_files,
                'authors_count': len(unique_authors)
            }
            
        except Exception as e:
            self.db.rollback()
            print(f"Error analyzing day {target_date}: {e}")
            return None
    
    def _calculate_daily_stats_from_commits(self, target_date: date):
        """Calculate and store daily author stats from commits for a specific date."""
        from sqlalchemy import func, and_
        
        # Query commits for the target date
        commits_query = self.db.query(Commit).filter(
            and_(
                Commit.repository_id == self.repository.id,
                func.date(Commit.commit_datetime) == target_date
            )
        )
        
        # Group by author and calculate stats
        author_stats = {}
        
        for commit in commits_query:
            # Primary author stats
            if commit.author_id not in author_stats:
                author_stats[commit.author_id] = {
                    'commits_count': 0,
                    'added_lines': 0,
                    'deleted_lines': 0,
                    'files_changed': 0
                }
            
            author_stats[commit.author_id]['commits_count'] += 1
            author_stats[commit.author_id]['added_lines'] += commit.added_lines
            author_stats[commit.author_id]['deleted_lines'] += commit.deleted_lines
            author_stats[commit.author_id]['files_changed'] += commit.files_changed
            
            # Co-author stats (same as primary author for co-authored commits)
            co_authors = self.db.query(CommitCoAuthor).filter(
                CommitCoAuthor.commit_id == commit.id
            ).all()
            
            for co_author_rel in co_authors:
                if co_author_rel.author_id not in author_stats:
                    author_stats[co_author_rel.author_id] = {
                        'commits_count': 0,
                        'added_lines': 0,
                        'deleted_lines': 0,
                        'files_changed': 0
                    }
                
                author_stats[co_author_rel.author_id]['commits_count'] += 1
                author_stats[co_author_rel.author_id]['added_lines'] += commit.added_lines
                author_stats[co_author_rel.author_id]['deleted_lines'] += commit.deleted_lines
                author_stats[co_author_rel.author_id]['files_changed'] += commit.files_changed
        
        # Store or update daily stats
        for author_id, stats in author_stats.items():
            existing = self.db.query(DailyAuthorStats).filter(
                DailyAuthorStats.repository_id == self.repository.id,
                DailyAuthorStats.author_id == author_id,
                DailyAuthorStats.date == target_date
            ).first()
            
            if existing:
                # Update existing record
                existing.commits_count = stats['commits_count']
                existing.added_lines = stats['added_lines']
                existing.deleted_lines = stats['deleted_lines']
                existing.files_changed = stats['files_changed']
            else:
                # Create new record
                daily_stat = DailyAuthorStats(
                    repository_id=self.repository.id,
                    author_id=author_id,
                    date=target_date,
                    commits_count=stats['commits_count'],
                    added_lines=stats['added_lines'],
                    deleted_lines=stats['deleted_lines'],
                    files_changed=stats['files_changed']
                )
                self.db.add(daily_stat)
    
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