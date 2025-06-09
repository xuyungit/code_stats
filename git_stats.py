#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import argparse
from datetime import date, datetime, timedelta
import re
import os

def get_git_stats(repo_path, days_ago):
    """
    Calculates git statistics for a given repository and time period.

    Args:
        repo_path (str): The path to the git repository.
        days_ago (int): The number of days to look back.

    Returns:
        dict: A dictionary containing 'added_lines', 'deleted_lines', 
              'total_files_changed', and 'commits_count', or None if an error occurs.
    """
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        print(f"Error: {repo_path} is not a valid git repository.")
        return None

    since_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    added_lines = 0
    deleted_lines = 0
    total_files_changed = 0
    commits_count = 0

    try:
        # Get commit hashes within the time period
        commit_hashes_cmd = [
            'git', 'log', 
            f'--since={since_date}', 
            '--pretty=format:%H'
        ]
        result = subprocess.run(commit_hashes_cmd, cwd=repo_path, capture_output=True, text=True, check=True)
        commit_hashes = result.stdout.strip().split('\n')
        if not commit_hashes or not commit_hashes[0]: # Handle case with no commits
            commits_count = 0
        else:
            commits_count = len(commit_hashes)





        # If there are commits in the period, calculate diff from start of period to HEAD
        if commits_count > 0:
            # Find the commit hash at the beginning of the period
            # `git rev-list -n 1 --before="{since_date} 00:00:00" HEAD` gives the last commit *before* the period starts.
            # If no such commit, it means all history is within the period, so diff from the initial commit's parent (empty tree).

            # Get the hash of the commit just before our 'since_date'
            before_since_date_commit_cmd = ['git', 'rev-list', '-n', '1', f'--before={since_date}', 'HEAD']
            before_commit_result = subprocess.run(before_since_date_commit_cmd, cwd=repo_path, capture_output=True, text=True)

            start_commit_hash = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" # Git's empty tree hash for initial commit scenario
            if before_commit_result.returncode == 0 and before_commit_result.stdout.strip():
                start_commit_hash = before_commit_result.stdout.strip()
            elif before_commit_result.returncode != 0:
                 print(f"Warning: 'git rev-list --before' (before_since_date_commit_cmd) failed with code {before_commit_result.returncode}. Stderr: {before_commit_result.stderr.strip() if before_commit_result.stderr else 'N/A'}")

            diff_cmd = ['git', 'diff', '--shortstat', start_commit_hash, 'HEAD']
            diff_result = subprocess.run(diff_cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            diff_output = diff_result.stdout.strip()

            if diff_output:
                # Example: " 1 file changed, 1 insertion(+), 1 deletion(-)"
                # Or: " 2 files changed, 10 insertions(+)"
                # Or: " 1 file changed, 5 deletions(-)"
                files_changed_match = re.search(r'(\d+) files? changed', diff_output) # Corrected regex: r'(\d+) files? changed'
                insertions_match = re.search(r'(\d+) insertions?\(\+\)', diff_output) # Corrected regex: r'(\d+) insertions?\(\+\)'
                deletions_match = re.search(r'(\d+) deletions?\(-\)', diff_output) # Corrected regex: r'(\d+) deletions?\(\-\)'

                if files_changed_match:
                    total_files_changed = int(files_changed_match.group(1))
                if insertions_match:
                    added_lines = int(insertions_match.group(1))
                if deletions_match:
                    deleted_lines = int(deletions_match.group(1))

        # If commits_count is 0, the above diff logic might not run or give 0, which is correct.

    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: git command not found. Is git installed and in your PATH?")
        return None

    return {
        'added_lines': added_lines,
        'deleted_lines': deleted_lines,
        'total_files_changed': total_files_changed,
        'commits_count': commits_count
    }

def get_daily_git_stats(repo_path: str, target_date: date):
    """
    Calculates git statistics for a given repository for a specific day.

    Args:
        repo_path (str): The path to the git repository.
        target_date (date): The specific date to get statistics for.

    Returns:
        dict: A dictionary containing 'added_lines', 'deleted_lines', 
              'total_files_changed', and 'commits_count', or None if an error occurs.
    """
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        # This check might be redundant if main already checks, but good for standalone use
        # print(f"Error: {repo_path} is not a valid git repository.") 
        return None

    added_lines = 0
    deleted_lines = 0
    total_files_changed = 0
    commits_count = 0

    # Define the time range for the target_date
    since_datetime_str = target_date.strftime('%Y-%m-%d 00:00:00')
    # --until is exclusive, so we use the start of the next day
    until_datetime_str = (target_date + timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')

    try:
        # Get commit hashes for the day, oldest first
        commit_hashes_cmd = [
            'git', 'log',
            f'--since={since_datetime_str}',
            f'--until={until_datetime_str}',
            '--pretty=format:%H',
            '--reverse'  # Get oldest commits first for the day
        ]
        result = subprocess.run(commit_hashes_cmd, cwd=repo_path, capture_output=True, text=True, check=False) # check=False to handle no commits
        
        if result.returncode != 0:
            if "your current branch 'master' does not have any commits yet" in result.stderr:
                # Handle empty repo or branch with no commits gracefully
                pass # Stats will remain 0
            else:
                print(f"Git log command failed for {target_date.strftime('%Y-%m-%d')}: {result.stderr.strip()}")
                return None
        
        commit_hashes = result.stdout.strip().split('\n')
        if not commit_hashes or not commit_hashes[0]:
            commits_count = 0
        else:
            commits_count = len(commit_hashes)

        if commits_count > 0:
            first_commit_hash_of_day = commit_hashes[0]
            last_commit_hash_of_day = commit_hashes[-1]

            # Determine the reference commit to diff against
            # This should be the commit *before* the first_commit_hash_of_day
            start_ref = ""
            try:
                # Try to get the parent of the first commit of the day
                parent_check_cmd = ['git', 'rev-parse', f'{first_commit_hash_of_day}^']
                parent_result = subprocess.run(parent_check_cmd, cwd=repo_path, capture_output=True, text=True, check=True)
                start_ref = parent_result.stdout.strip()
            except subprocess.CalledProcessError:
                # This happens if first_commit_hash_of_day is the initial commit (has no parent)
                # In this case, we diff against the empty tree hash
                start_ref = "4b825dc642cb6eb9a060e54bf8d69288fbee4904" 
            
            # Diff from the state before the first commit of the day to the last commit of the day
            diff_cmd = ['git', 'diff', '--shortstat', start_ref, last_commit_hash_of_day]
            diff_result = subprocess.run(diff_cmd, cwd=repo_path, capture_output=True, text=True, check=True)
            diff_output = diff_result.stdout.strip()

            if diff_output:
                files_changed_match = re.search(r'(\d+) files? changed', diff_output)
                insertions_match = re.search(r'(\d+) insertions?\(\+\)', diff_output)
                deletions_match = re.search(r'(\d+) deletions?\(-\)', diff_output)

                if files_changed_match:
                    total_files_changed = int(files_changed_match.group(1))
                if insertions_match:
                    added_lines = int(insertions_match.group(1))
                if deletions_match:
                    deleted_lines = int(deletions_match.group(1))

    except subprocess.CalledProcessError as e:
        print(f"Git command failed for {target_date.strftime('%Y-%m-%d')}: {e}")
        print(f"Stderr: {e.stderr}")
        return None
    except FileNotFoundError:
        print("Error: git command not found. Is git installed and in your PATH?")
        return None # Or raise an exception

    return {
        'added_lines': added_lines,
        'deleted_lines': deleted_lines,
        'total_files_changed': total_files_changed,
        'commits_count': commits_count
    }


def main():
    parser = argparse.ArgumentParser(
        description='Calculate code statistics for a git repository over a specified period.'
    )
    parser.add_argument('repo_path', type=str, help='Path to the git repository.')
    parser.add_argument(
        '--days', 
        type=int, 
        default=7, 
        help='Number of recent days to show daily statistics for. Default is 7.'
    )

    args = parser.parse_args()

    if not os.path.isdir(args.repo_path):
        print(f"Error: Repository path {args.repo_path} does not exist or is not a directory.")
        return
    
    if not os.path.isdir(os.path.join(args.repo_path, '.git')):
        print(f"Error: {args.repo_path} is not a valid git repository.")
        return

    base_date = datetime.now().date() # Use date part for daily calculations
    print(f"\n--- Daily Git Repository Statistics for the last {args.days} day(s) ---")
    print(f"Repository: {os.path.abspath(args.repo_path)}")
    print(f"-----------------------------------------------------")

    for i in range(args.days):
        # Iterate from today (i=0) to N-1 days ago
        current_target_date = base_date - timedelta(days=i)
        print(f"\nDate: {current_target_date.strftime('%Y-%m-%d')}")
        
        stats = get_daily_git_stats(args.repo_path, current_target_date)

        if stats:
            print(f"  Commits: {stats['commits_count']}")
            print(f"  Files changed: {stats['total_files_changed']}")
            print(f"  Lines added: {stats['added_lines']}")
            print(f"  Lines deleted: {stats['deleted_lines']}")
            net_change = stats['added_lines'] - stats['deleted_lines']
            print(f"  Net lines change:  {net_change} ({'+' if net_change >= 0 else ''}{net_change})")
            total_activity = stats['added_lines'] + stats['deleted_lines'] 
            print(f"  Total line activity: {total_activity}")
        else:
            # get_daily_git_stats might have printed an error, or it might be a day with no activity
            # If it returned None, an error was printed. If it returned 0 stats, it means no activity.
            # We can refine this if needed, but for now, a general message or relying on get_daily_git_stats's prints.
            print(f"  No activity or error fetching stats for this day.")
            
    print(f"-----------------------------------------------------")

if __name__ == '__main__':
    main()