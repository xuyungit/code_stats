#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class GitStats:
    """Data class for git statistics."""
    added_lines: int = 0
    deleted_lines: int = 0
    total_files_changed: int = 0
    commits_count: int = 0
    
    @property
    def net_change(self) -> int:
        """Calculate net line change (added - deleted)."""
        return self.added_lines - self.deleted_lines
    
    @property
    def total_activity(self) -> int:
        """Calculate total line activity (added + deleted)."""
        return self.added_lines + self.deleted_lines


@dataclass
class AuthorStats:
    """Data class for author-specific git statistics."""
    name: str
    commits_count: int = 0
    added_lines: int = 0
    deleted_lines: int = 0
    files_changed: Set[str] = None
    
    def __post_init__(self):
        if self.files_changed is None:
            self.files_changed = set()
    
    @property
    def total_files_changed(self) -> int:
        """Get count of files changed by this author."""
        return len(self.files_changed)
    
    @property
    def net_change(self) -> int:
        """Calculate net line change (added - deleted)."""
        return self.added_lines - self.deleted_lines
    
    @property
    def total_activity(self) -> int:
        """Calculate total line activity (added + deleted)."""
        return self.added_lines + self.deleted_lines


def parse_shortstat_output(shortstat: str) -> Tuple[int, int, int]:
    """
    Parses git diff --shortstat output to extract statistics.
    
    Args:
        shortstat: Output from git diff --shortstat command
        
    Returns:
        Tuple of (files_changed, insertions, deletions)
    """
    files_changed = 0
    insertions = 0
    deletions = 0
    
    if shortstat:
        files_match = re.search(r'(\d+) files? changed', shortstat)
        insertions_match = re.search(r'(\d+) insertions?\(\+\)', shortstat)
        deletions_match = re.search(r'(\d+) deletions?\(-\)', shortstat)
        
        if files_match:
            files_changed = int(files_match.group(1))
        if insertions_match:
            insertions = int(insertions_match.group(1))
        if deletions_match:
            deletions = int(deletions_match.group(1))
    
    return files_changed, insertions, deletions


def parse_commit_diff_stats(diff_output: str) -> Tuple[int, int, Set[str]]:
    """
    Parses git show --stat output to extract line changes and file names.
    
    Args:
        diff_output: Output from git show --stat command
        
    Returns:
        Tuple of (insertions, deletions, files_changed_set)
    """
    insertions = 0
    deletions = 0
    files_changed = set()
    
    if not diff_output:
        return insertions, deletions, files_changed
    
    lines = diff_output.split('\n')
    for line in lines:
        # Look for the summary line with insertions/deletions
        if 'insertion' in line or 'deletion' in line:
            insertions_match = re.search(r'(\d+) insertions?\(\+\)', line)
            deletions_match = re.search(r'(\d+) deletions?\(-\)', line)
            
            if insertions_match:
                insertions += int(insertions_match.group(1))
            if deletions_match:
                deletions += int(deletions_match.group(1))
        # Look for file change lines (filename | changes)
        elif line.strip() and '|' in line and not line.startswith(' '):
            file_parts = line.split('|')
            if len(file_parts) >= 2:
                filename = file_parts[0].strip()
                files_changed.add(filename)
    
    return insertions, deletions, files_changed


def create_author_stats_dict() -> Dict[str, AuthorStats]:
    """Creates an empty dictionary for storing author statistics."""
    return {}


def add_author_commit_stats(author_stats: Dict[str, AuthorStats], 
                          author_email: str, 
                          author_name: str,
                          added: int = 0,
                          deleted: int = 0,
                          files: Set[str] = None) -> None:
    """
    Adds commit statistics for an author.
    
    Args:
        author_stats: Dictionary to update
        author_email: Author's email address
        author_name: Author's name
        added: Lines added in this commit
        deleted: Lines deleted in this commit
        files: Set of files changed in this commit
    """
    if author_email not in author_stats:
        author_stats[author_email] = AuthorStats(name=author_name)
    
    stats = author_stats[author_email]
    stats.commits_count += 1
    stats.added_lines += added
    stats.deleted_lines += deleted
    
    if files:
        stats.files_changed.update(files)


def finalize_author_stats(author_stats: Dict[str, AuthorStats]) -> Dict[str, dict]:
    """
    Converts AuthorStats objects to dictionaries for backward compatibility.
    
    Args:
        author_stats: Dictionary of AuthorStats objects
        
    Returns:
        Dictionary with author statistics in the original format
    """
    result = {}
    for email, stats in author_stats.items():
        result[email] = {
            'name': stats.name,
            'commits_count': stats.commits_count,
            'added_lines': stats.added_lines,
            'deleted_lines': stats.deleted_lines,
            'total_files_changed': stats.total_files_changed
        }
    return result


def sort_authors_by_activity(author_stats: Dict[str, dict]) -> list:
    """
    Sorts authors by total activity (lines added + deleted).
    
    Args:
        author_stats: Dictionary of author statistics
        
    Returns:
        List of (author_email, stats) tuples sorted by activity
    """
    return sorted(author_stats.items(), 
                  key=lambda x: x[1]['added_lines'] + x[1]['deleted_lines'], 
                  reverse=True)