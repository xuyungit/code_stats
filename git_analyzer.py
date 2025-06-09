#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import date, timedelta
from typing import Dict, Optional, List

from git_utils import (
    validate_git_repository, get_commits_in_period, get_commits_with_authors,
    get_diff_shortstat, get_commit_diff_stats, get_commit_before_date,
    get_commit_parent, format_date_for_git, get_days_ago_date, EMPTY_TREE_HASH
)
from stats_parser import (
    GitStats, parse_shortstat_output, parse_commit_diff_stats,
    create_author_stats_dict, add_author_commit_stats, finalize_author_stats
)


class GitAnalyzer:
    """Main class for analyzing git repository statistics."""
    
    def __init__(self, repo_path: str):
        """
        Initialize the analyzer with a repository path.
        
        Args:
            repo_path: Path to the git repository
            
        Raises:
            GitError: If the repository is invalid
        """
        validate_git_repository(repo_path)
        self.repo_path = repo_path
    
    def get_period_stats(self, days_ago: int) -> Optional[Dict]:
        """
        Gets overall statistics for a time period.
        
        Args:
            days_ago: Number of days to look back
            
        Returns:
            Dictionary with statistics or None if error occurs
        """
        try:
            since_date = get_days_ago_date(days_ago)
            commits = get_commits_in_period(self.repo_path, since_date)
            
            if not commits:
                return {
                    'added_lines': 0,
                    'deleted_lines': 0,
                    'total_files_changed': 0,
                    'commits_count': 0
                }
            
            # Get commit before the period started
            before_commit = get_commit_before_date(self.repo_path, since_date)
            start_ref = before_commit if before_commit else EMPTY_TREE_HASH
            
            # Get diff from start of period to HEAD
            shortstat = get_diff_shortstat(self.repo_path, start_ref, 'HEAD')
            files_changed, added_lines, deleted_lines = parse_shortstat_output(shortstat)
            
            return {
                'added_lines': added_lines,
                'deleted_lines': deleted_lines,
                'total_files_changed': files_changed,
                'commits_count': len(commits)
            }
            
        except Exception as e:
            print(f"Error getting period stats: {e}")
            return None
    
    def get_author_stats_period(self, days_ago: int) -> Optional[Dict]:
        """
        Gets author statistics for a time period.
        
        Args:
            days_ago: Number of days to look back
            
        Returns:
            Dictionary with author statistics or None if error occurs
        """
        try:
            since_date = get_days_ago_date(days_ago)
            commits = get_commits_with_authors(self.repo_path, since_date)
            
            if not commits:
                return {}
            
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
            
            return finalize_author_stats(author_stats)
            
        except Exception as e:
            print(f"Error getting author stats: {e}")
            return None
    
    def get_daily_stats(self, target_date: date) -> Optional[Dict]:
        """
        Gets overall statistics for a specific day.
        
        Args:
            target_date: The date to analyze
            
        Returns:
            Dictionary with statistics or None if error occurs
        """
        try:
            since_datetime = format_date_for_git(target_date)
            until_datetime = format_date_for_git(target_date + timedelta(days=1))
            
            commits = get_commits_in_period(self.repo_path, since_datetime, until_datetime)
            
            if not commits:
                return {
                    'added_lines': 0,
                    'deleted_lines': 0,
                    'total_files_changed': 0,
                    'commits_count': 0
                }
            
            # Get the range of commits for the day
            first_commit = commits[0]
            last_commit = commits[-1]
            
            # Get the commit before the first commit of the day
            start_ref = get_commit_parent(self.repo_path, first_commit)
            if not start_ref:
                start_ref = EMPTY_TREE_HASH
            
            # Get diff from before first commit to last commit of the day
            shortstat = get_diff_shortstat(self.repo_path, start_ref, last_commit)
            files_changed, added_lines, deleted_lines = parse_shortstat_output(shortstat)
            
            return {
                'added_lines': added_lines,
                'deleted_lines': deleted_lines,
                'total_files_changed': files_changed,
                'commits_count': len(commits)
            }
            
        except Exception as e:
            print(f"Error getting daily stats for {target_date}: {e}")
            return None
    
    def get_daily_author_stats(self, target_date: date) -> Optional[Dict]:
        """
        Gets author statistics for a specific day.
        
        Args:
            target_date: The date to analyze
            
        Returns:
            Dictionary with author statistics or None if error occurs
        """
        try:
            since_datetime = format_date_for_git(target_date)
            until_datetime = format_date_for_git(target_date + timedelta(days=1))
            
            commits = get_commits_with_authors(self.repo_path, since_datetime, until_datetime)
            
            if not commits:
                return {}
            
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
            
            return finalize_author_stats(author_stats)
            
        except Exception as e:
            print(f"Error getting daily author stats for {target_date}: {e}")
            return None
    
    def get_daily_breakdown(self, days: int) -> List[Dict]:
        """
        Gets daily statistics breakdown for multiple days.
        
        Args:
            days: Number of recent days to analyze
            
        Returns:
            List of dictionaries with daily statistics
        """
        results = []
        base_date = date.today()
        
        for i in range(days):
            current_date = base_date - timedelta(days=i)
            stats = self.get_daily_stats(current_date)
            results.append({
                'date': current_date,
                'stats': stats
            })
        
        return results
    
    def get_daily_author_breakdown(self, days: int) -> List[Dict]:
        """
        Gets daily author statistics breakdown for multiple days.
        
        Args:
            days: Number of recent days to analyze
            
        Returns:
            List of dictionaries with daily author statistics
        """
        results = []
        base_date = date.today()
        
        for i in range(days):
            current_date = base_date - timedelta(days=i)
            author_stats = self.get_daily_author_stats(current_date)
            results.append({
                'date': current_date,
                'author_stats': author_stats
            })
        
        return results