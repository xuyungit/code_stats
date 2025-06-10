#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import os
from typing import Optional, List
from datetime import datetime, timedelta, date


class GitError(Exception):
    """Custom exception for git-related errors."""
    pass


def validate_git_repository(repo_path: str) -> None:
    """
    Validates that the given path is a git repository.
    
    Args:
        repo_path: Path to check
        
    Raises:
        GitError: If the path is not a valid git repository
    """
    if not os.path.isdir(repo_path):
        raise GitError(f"Repository path {repo_path} does not exist or is not a directory.")
    
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        raise GitError(f"{repo_path} is not a valid git repository.")


def run_git_command(cmd: List[str], repo_path: str, check: bool = True) -> subprocess.CompletedProcess:
    """
    Executes a git command in the specified repository.
    
    Args:
        cmd: Git command and arguments as a list
        repo_path: Path to the git repository
        check: Whether to raise an exception on non-zero exit code
        
    Returns:
        CompletedProcess instance
        
    Raises:
        GitError: If the git command fails or git is not found
    """
    try:
        result = subprocess.run(cmd, cwd=repo_path, capture_output=True, text=True, check=check)
        return result
    except subprocess.CalledProcessError as e:
        raise GitError(f"Git command failed: {e}\nStderr: {e.stderr}")
    except FileNotFoundError:
        raise GitError("git command not found. Is git installed and in your PATH?")


def get_commits_in_period(repo_path: str, since_date: str, until_date: Optional[str] = None) -> List[str]:
    """
    Gets commit hashes for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        List of commit hashes
    """
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    commit_hashes = result.stdout.strip().split('\n')
    return [h for h in commit_hashes if h]  # Filter out empty strings


def get_commits_with_authors(repo_path: str, since_date: str, until_date: Optional[str] = None) -> List[dict]:
    """
    Gets commits with author information for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        List of dictionaries with commit hash, author email, and author name
    """
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H|%ae|%an']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    if not result.stdout.strip():
        return []
    
    commits = []
    for line in result.stdout.strip().split('\n'):
        parts = line.split('|')
        if len(parts) >= 3:
            commits.append({
                'hash': parts[0],
                'author_email': parts[1],
                'author_name': parts[2]
            })
    
    return commits


def get_commits_detailed(repo_path: str, since_date: str, until_date: Optional[str] = None) -> List[dict]:
    """
    Gets detailed commit information including message and datetime for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        
    Returns:
        List of dictionaries with commit hash, author email, author name, message, and datetime
    """
    # Format: hash|author_email|author_name|iso_datetime|commit_message
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H|%ae|%an|%aI|%B']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    if not result.stdout.strip():
        return []
    
    commits = []
    # Split by commit separator (double newline followed by hash pattern)
    commit_blocks = result.stdout.strip().split('\n\n')
    
    for block in commit_blocks:
        if not block.strip():
            continue
            
        lines = block.strip().split('\n')
        if not lines:
            continue
            
        # First line contains hash|email|name|datetime
        header_parts = lines[0].split('|', 3)
        if len(header_parts) >= 4:
            # Message is everything after the header line
            message_lines = lines[1:] if len(lines) > 1 else ['']
            message = '\n'.join(message_lines).strip()
            
            commits.append({
                'hash': header_parts[0],
                'author_email': header_parts[1],
                'author_name': header_parts[2],
                'datetime': header_parts[3],
                'message': message
            })
    
    return commits


def get_diff_shortstat(repo_path: str, from_ref: str, to_ref: str) -> str:
    """
    Gets the shortstat output for a diff between two git references.
    
    Args:
        repo_path: Path to the git repository
        from_ref: Starting reference (commit hash, branch, etc.)
        to_ref: Ending reference (commit hash, branch, etc.)
        
    Returns:
        Shortstat output string
    """
    cmd = ['git', 'diff', '--shortstat', from_ref, to_ref]
    result = run_git_command(cmd, repo_path)
    return result.stdout.strip()


def get_commit_diff_stats(repo_path: str, commit_hash: str) -> str:
    """
    Gets the diff stats for a specific commit.
    
    Args:
        repo_path: Path to the git repository
        commit_hash: The commit hash to analyze
        
    Returns:
        Diff stats output string
    """
    cmd = ['git', 'show', '--stat', '--format=', commit_hash]
    result = run_git_command(cmd, repo_path)
    return result.stdout.strip()


def get_commit_before_date(repo_path: str, before_date: str) -> Optional[str]:
    """
    Gets the last commit before a specific date.
    
    Args:
        repo_path: Path to the git repository
        before_date: Date in YYYY-MM-DD format
        
    Returns:
        Commit hash if found, None otherwise
    """
    cmd = ['git', 'rev-list', '-n', '1', f'--before={before_date}', 'HEAD']
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return None


def get_commit_parent(repo_path: str, commit_hash: str) -> Optional[str]:
    """
    Gets the parent commit hash for a given commit.
    
    Args:
        repo_path: Path to the git repository
        commit_hash: The commit hash
        
    Returns:
        Parent commit hash if exists, None if it's the initial commit
    """
    cmd = ['git', 'rev-parse', f'{commit_hash}^']
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def format_date_for_git(target_date: date) -> str:
    """
    Formats a date object for git commands.
    
    Args:
        target_date: Date to format
        
    Returns:
        Formatted date string for git
    """
    return target_date.strftime('%Y-%m-%d 00:00:00')


def get_days_ago_date(days_ago: int) -> str:
    """
    Gets a date string for N days ago.
    
    Args:
        days_ago: Number of days to go back
        
    Returns:
        Date string in YYYY-MM-DD format
    """
    return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')


# Git's empty tree hash for diffs against initial commits
EMPTY_TREE_HASH = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"