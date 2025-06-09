# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains tools for analyzing git repository code activity and statistics. The tools help track development metrics like commits, line changes, and file modifications over time.

## Architecture

- Python-based command-line tools that interface with git repositories via subprocess calls
- Modular functions for different time-based analysis (period ranges vs daily breakdowns)
- Uses git's native commands for data extraction and diff analysis

## Key Features

- Analyze code activity over configurable time periods
- Daily breakdown of development statistics
- Track commits, lines added/deleted, files changed, and net activity
- Handle edge cases like empty repositories and initial commits

## Running Tools

```bash
# Basic usage with default settings
python git_stats.py /path/to/repo

# Custom time period analysis
python git_stats.py /path/to/repo --days N
```

## Development Guidelines

- Python 3.13+ required
- All git operations should handle subprocess errors gracefully
- Maintain compatibility with various git repository states (empty, single commit, etc.)
