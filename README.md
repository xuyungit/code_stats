<!-- filepath: /Users/xuyun/AI/code_stats/README.md -->
# Code Stats

## Overview

This project provides a Python script (`git_stats.py`) to analyze Git repository activity. It calculates and displays statistics such as the number of commits, files changed, lines added, and lines deleted over a specified period. The primary use case is to get a daily breakdown of development activity for the last N days.

## Features

- **Daily Statistics:** Provides a day-by-day summary of Git activity.
- **Configurable Period:** Allows specifying the number of recent days to analyze.
- **Detailed Metrics:** For each day, shows:
  - Number of commits
  - Number of files changed
  - Number of lines added
  - Number of lines deleted
  - Net line change
  - Total line activity (added + deleted)
- **Handles Various Git States:** Designed to work correctly with repositories in different states (e.g., new repositories, repositories with activity only within the queried period).

## Requirements

- Python 3.13+
- Git installed and accessible in your system's PATH.

## Usage

The script is run from the command line.

```bash
python git_stats.py <repo_path> [--days N]
```

**Arguments:**

- `repo_path`: (Required) The absolute or relative path to the Git repository you want to analyze.
- `--days N`: (Optional) The number of recent days for which to show daily statistics. Defaults to 7.

**Example:**

To analyze the last 7 days of activity in a repository located at `/path/to/your/repo`:

```bash
python git_stats.py /path/to/your/repo
```

To analyze the last 30 days of activity:

```bash
python git_stats.py /path/to/your/repo --days 30
```

## How it Works

The `git_stats.py` script performs the following main steps:

1. **Parses Arguments:** Reads the repository path and the number of days for analysis.
2. **Validates Repository:** Checks if the provided path is a valid Git repository.
3. **Iterates Through Days:** For each day in the specified range (from today backwards):
   - Determines the start and end timestamps for that specific day.
   - Uses `git log` to find commits made within that day.
   - If commits are found:
     - It identifies the first and last commit of that day.
     - It determines the state of the repository *before* the first commit of the day (either the parent of the first commit or the empty tree hash for initial commits).
     - It uses `git diff --shortstat` to compare the state before the first commit of the day with the state at the last commit of the day. This provides the lines added/deleted and files changed *specifically for that day's activity*.
   - If no commits are found for a day, it reports no activity.
4. **Prints Statistics:** Outputs the collected statistics for each day in a readable format.

The script relies on `subprocess` to execute Git commands and parses their output.

## `pyproject.toml`

The `pyproject.toml` file is configured for a basic Python project using modern packaging standards.

```toml
[project]
name = "code-stats"
version = "0.1.0"
description = "A Python utility to get daily Git statistics for a repository."
readme = "README.md"
requires-python = ">=3.13"
dependencies = [] # No external dependencies
```

## Future Enhancements (Potential)

- Aggregate statistics for the entire period (in addition to daily).
- Support for specific date ranges (not just "last N days").
- Author-specific statistics.
- Output in different formats (e.g., CSV, JSON).
- Ignoring specific files or directories from stats.

## Contribution

Feel free to fork the repository, make improvements, and submit pull requests.

## License

This project is open-source. (Please add a specific license file if desired, e.g., MIT, Apache 2.0).
