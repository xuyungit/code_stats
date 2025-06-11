# Multi-Branch Git Analysis

## Overview

The git statistics analyzer now supports analyzing commits across all branches in a repository, with intelligent deduplication and rebase handling.

## Key Features

### 1. All Branches Analysis
- By default, the analyzer examines commits from all branches, not just the current/default branch
- This ensures comprehensive statistics that include feature branches, release branches, etc.
- Controlled via `all_branches` parameter (default: `True`)

### 2. Commit Deduplication
- Commits that appear in multiple branches are only counted once
- Uses commit hash as the primary identifier
- Preserves order while removing duplicates

### 3. Rebase Detection
- Uses Git's `patch-id` to identify commits that have been rebased
- Patch-id remains stable even when commit hash changes due to rebase
- Database tracks both commit hash and patch-id
- When a rebased commit is detected:
  - Updates the commit hash to the new one
  - Preserves all statistics and relationships

## Implementation Details

### Modified Functions

1. **`get_commits_in_period()`**
   - Added `all_branches` parameter
   - Uses `git log --all` to include all branches
   - Returns unique list of commit hashes

2. **`get_commits_with_authors()`**
   - Added `all_branches` parameter
   - Deduplicates commits by hash
   - Maintains author information

3. **`get_commits_detailed()`**
   - Added `all_branches` parameter
   - Returns detailed commit info with deduplication

4. **`get_commit_patch_id()`**
   - New function to calculate stable patch-id
   - Uses `git patch-id --stable`
   - Returns None if patch-id cannot be calculated

### Database Schema Changes

Added `patch_id` column to the `commits` table:
```sql
ALTER TABLE commits ADD COLUMN patch_id VARCHAR(40);
CREATE INDEX idx_commits_patch_id ON commits(patch_id);
```

### Analyzer Updates

The `WebGitAnalyzer` now:
1. Calculates patch-id for each commit
2. Checks for existing commits by both hash and patch-id
3. Updates commit hash when rebase is detected
4. Prevents duplicate storage of the same logical commit

## Usage

The feature is automatically enabled for all git analysis operations:

```python
# In git_analyzer.py
analyzer = GitAnalyzer(repo_path)
stats = analyzer.get_period_stats(7)  # Analyzes all branches

# In web service
analyzer = WebGitAnalyzer(db, repository)
analyzer.analyze_single_day(date.today())  # Includes all branches
```

## Benefits

1. **Complete Statistics**: No commits are missed from feature branches
2. **Accurate Counts**: No double-counting of merged commits
3. **Rebase Resilient**: Statistics remain consistent even after rebases
4. **Historical Integrity**: Past analyses remain valid after repository restructuring

## Notes

- The `--all` flag in git commands may slightly increase analysis time for large repositories
- Patch-id calculation adds minimal overhead
- Deduplication is performed in-memory for efficiency