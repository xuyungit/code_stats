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


def get_commits_in_period(repo_path: str, since_date: str, until_date: Optional[str] = None, all_branches: bool = True) -> List[str]:
    """
    Gets commit hashes for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        all_branches: Whether to check all branches (default True)
        
    Returns:
        List of unique commit hashes
    """
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    if all_branches:
        cmd.append('--all')  # Include all branches
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    commit_hashes = result.stdout.strip().split('\n')
    # Use a set to automatically deduplicate commits that appear in multiple branches
    unique_hashes = list(dict.fromkeys(h for h in commit_hashes if h))  # Preserves order
    return unique_hashes


def get_commits_with_authors(repo_path: str, since_date: str, until_date: Optional[str] = None, all_branches: bool = True) -> List[dict]:
    """
    Gets commits with author information for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        all_branches: Whether to check all branches (default True)
        
    Returns:
        List of dictionaries with commit hash, author email, and author name
    """
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H|%ae|%an']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    if all_branches:
        cmd.append('--all')  # Include all branches
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    if not result.stdout.strip():
        return []
    
    commits = []
    seen_hashes = set()
    for line in result.stdout.strip().split('\n'):
        parts = line.split('|')
        if len(parts) >= 3 and parts[0] not in seen_hashes:
            commits.append({
                'hash': parts[0],
                'author_email': parts[1],
                'author_name': parts[2]
            })
            seen_hashes.add(parts[0])
    
    return commits


def get_commits_detailed(repo_path: str, since_date: str, until_date: Optional[str] = None, all_branches: bool = True) -> List[dict]:
    """
    Gets detailed commit information including message and datetime for a specific time period.
    
    Args:
        repo_path: Path to the git repository
        since_date: Start date in YYYY-MM-DD format
        until_date: End date in YYYY-MM-DD format (optional)
        all_branches: Whether to check all branches (default True)
        
    Returns:
        List of dictionaries with commit hash, author email, author name, message, and datetime
    """
    # Use a unique separator to avoid confusion
    cmd = ['git', 'log', f'--since={since_date}', '--pretty=format:%H|||%ae|||%an|||%aI|||%B|||COMMIT_END|||']
    if until_date:
        cmd.append(f'--until={until_date}')
    
    if all_branches:
        cmd.append('--all')  # Include all branches
    
    result = run_git_command(cmd, repo_path, check=False)
    
    if result.returncode != 0:
        if "your current branch 'master' does not have any commits yet" in result.stderr:
            return []
        else:
            raise GitError(f"Git log command failed: {result.stderr.strip()}")
    
    if not result.stdout.strip():
        return []
    
    commits = []
    seen_hashes = set()
    # Split by commit separator
    commit_blocks = result.stdout.strip().split('|||COMMIT_END|||')
    
    for block in commit_blocks:
        if not block.strip():
            continue
            
        # Split the commit data
        parts = block.strip().split('|||')
        if len(parts) >= 5:
            hash_val = parts[0]
            if hash_val not in seen_hashes:
                author_email = parts[1] 
                author_name = parts[2]
                datetime_val = parts[3]
                message = parts[4].strip() if len(parts) > 4 else ''
                
                commits.append({
                    'hash': hash_val,
                    'author_email': author_email,
                    'author_name': author_name,
                    'datetime': datetime_val,
                    'message': message
                })
                seen_hashes.add(hash_val)
    
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


def get_commit_content_hash(repo_path: str, commit_hash: str) -> str:
    """
    Gets a content-based hash for a commit that remains stable across rebases.
    This uses the commit's tree hash combined with author info and message.
    
    Args:
        repo_path: Path to the git repository
        commit_hash: The commit hash to analyze
        
    Returns:
        A stable content hash for the commit
    """
    # Get tree hash, author, and subject (first line of message)
    cmd = ['git', 'show', '--format=%T|%ae|%at|%s', '-s', commit_hash]
    result = run_git_command(cmd, repo_path)
    
    if result.returncode == 0:
        return result.stdout.strip()
    return ""


def get_commit_patch_id(repo_path: str, commit_hash: str) -> Optional[str]:
    """
    Gets the patch-id for a commit, which is stable across rebases.
    The patch-id is a hash of the changes introduced by the commit.
    
    Args:
        repo_path: Path to the git repository
        commit_hash: The commit hash to analyze
        
    Returns:
        The patch-id if successful, None otherwise
    """
    # Generate patch and compute patch-id
    cmd1 = ['git', 'show', commit_hash]
    cmd2 = ['git', 'patch-id', '--stable']
    
    try:
        # Run first command
        result1 = subprocess.run(cmd1, cwd=repo_path, capture_output=True, text=True)
        if result1.returncode != 0:
            return None
            
        # Pipe to second command
        result2 = subprocess.run(cmd2, cwd=repo_path, input=result1.stdout, 
                               capture_output=True, text=True)
        if result2.returncode == 0 and result2.stdout:
            # patch-id output format: "<patch-id> <commit-id>"
            return result2.stdout.strip().split()[0]
    except Exception:
        pass
    
    return None


def git_fetch(repo_path: str, remote: str = None, timeout: int = 300) -> bool:
    """
    Fetches latest changes from remote repository.
    
    Args:
        repo_path: Path to the git repository
        remote: Specific remote to fetch from (None for all remotes)
        timeout: Timeout in seconds for the fetch operation (default 5 minutes)
        
    Returns:
        True if fetch succeeded, False otherwise
        
    Note:
        This function is designed to fail gracefully - analysis can continue
        with local data if fetch fails.
    """
    validate_git_repository(repo_path)
    
    # Build fetch command
    cmd = ['git', 'fetch']
    if remote:
        cmd.append(remote)
    else:
        # Fetch all remotes
        cmd.append('--all')
    
    # Add progress flag for better UX
    cmd.append('--progress')
    
    try:
        # Run with timeout
        result = subprocess.run(
            cmd, 
            cwd=repo_path, 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            check=False
        )
        
        if result.returncode == 0:
            return True
        else:
            # Log the error but don't raise - allow analysis to continue
            error_msg = result.stderr.strip() or result.stdout.strip()
            print(f"Git fetch warning: {error_msg}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"Git fetch timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"Git fetch error: {str(e)}")
        return False


# Git's empty tree hash for diffs against initial commits
EMPTY_TREE_HASH = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"