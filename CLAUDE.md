# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a web-based service for analyzing git repository code activity and statistics. Originally a command-line tool, it has been expanded into a multi-user web service with REST API and database storage for tracking development metrics over time.

## Architecture

### Command-Line Tools (Original)
- Python-based CLI tools that interface with git repositories via subprocess calls
- Modular functions for different time-based analysis (period ranges vs daily breakdowns)
- Uses git's native commands for data extraction and diff analysis

### Web Service (Current)
- **Backend**: FastAPI-based REST API with SQLAlchemy ORM
- **Database**: SQLite (development) with migration path to PostgreSQL/MySQL
- **Authentication**: JWT-based user authentication
- **Data Model**: Day-based atomic storage with user/author separation
- **Analysis Engine**: Adapted existing git analysis logic for web service

## Key Features

### CLI Features
- Analyze code activity over configurable time periods
- Daily breakdown of development statistics
- Track commits, lines added/deleted, files changed, and net activity
- Handle edge cases like empty repositories and initial commits

### Web Service Features
- Multi-user support with secure authentication
- Repository management (add, update, delete repositories)
- Author tracking separate from system users
- AI coder detection and flagging capability
- Day-based statistics storage for flexible aggregation
- Database migration system for schema evolution
- RESTful API with automatic documentation

## Data Model Design

### Core Entities
- **Users**: System users who access the web interface
- **Authors**: Git commit authors (separate from users)
- **Repositories**: Git repositories managed by users
- **DailyAuthorStats**: Atomic daily statistics per author per repository

### Key Principles
- Day-based atomic storage - only daily author stats are stored
- All period/aggregated statistics are calculated from daily data
- Clear separation between system users and git authors
- Manual AI coder flagging (no automatic detection)
- Database schema versioning with migration support

## Running Tools

### CLI (Original)
```bash
# Basic usage with default settings
python git_stats.py /path/to/repo

# Custom time period analysis
python git_stats.py /path/to/repo --days N
```

### Web Service

virtual env of the backend is at .venv directory of the workspace
```bash
# Install dependencies and start development server
uv add xxx
uv run python backend/app/run.py

# API documentation at http://localhost:8000/docs
```

## Development Guidelines

### General
- Python 3.13+ required
- All git operations should handle subprocess errors gracefully
- Maintain compatibility with various git repository states (empty, single commit, etc.)

### Web Service Specific
- Use FastAPI with SQLAlchemy for new API endpoints
- Follow day-based storage pattern - avoid storing aggregated data
- Use migration system for all database schema changes
- Maintain user/author separation in data model
- Use JWT authentication for API security
- Write Pydantic schemas for request/response validation

### Database Migrations
- Create migration files in `backend/migrations/` with format `{version}_{description}.sql`
- Include both UP and DOWN migration SQL
- Test migrations before applying to production
- Use migration manager for all schema changes
