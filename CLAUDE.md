# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This repository contains a web-based service for analyzing git repository code activity and statistics. It's a multi-user web service with REST API and database storage for tracking development metrics over time.

## Memory Log

- Record important discussion keypoints and agreement with claude code into a markdown file in doc folder (create different files for different topics)

## Architecture

### Get statistics from git repositories

- Uses git's native commands for data extraction and diff analysis

### Web Service
- **Backend**: FastAPI-based REST API with SQLAlchemy ORM
- **Database**: SQLite (development) with migration path to PostgreSQL/MySQL
- **Authentication**: JWT-based user authentication
- **Data Model**: Day-based atomic storage with user/author separation
- **Analysis Engine**: Adapted existing git analysis logic for web service

## Key Features

### Git Analyze Features

- Analyze code activity over configurable time periods
- Daily breakdown of development statistics
- Track commits, lines added/deleted, files changed, and net activity
- Handle edge cases like empty repositories and initial commits
- **Multi-branch analysis**: Analyzes all branches by default with automatic deduplication
- **Rebase detection**: Uses git patch-id to track commits across rebases
- **Commit deduplication**: Ensures commits appearing in multiple branches are counted only once

### Web Service Features
- Multi-user support with JWT authentication
- Repository management (add, update, delete repositories) 
- Git analysis integration with job tracking
- Statistics API (single-repo and cross-repo with flexible filtering)
- Author tracking separate from system users
- Manual AI coder flagging capability
- Day-based atomic storage for flexible aggregation
- Database migration system for schema evolution
- RESTful API with automatic Swagger documentation

## Data Model Design

### Core Entities
- **Users**: System users who access the web interface
- **Authors**: Git commit authors (separate from users)
- **Repositories**: Git repositories managed by users
- **DailyAuthorStats**: Atomic daily statistics per author per repository

### Key Principles
- Day-based atomic storage - only daily author stats are stored
- All period/aggregated statistics are calculated from daily data at query time
- Clear separation between system users and git authors
- Manual AI coder flagging (no automatic detection)
- Database schema versioning with migration support
- Avoid storing computed fields (net_change, code_activities) to prevent data redundancy
- Date-indexed API responses for frontend time-series visualization
- Author ID references only in responses, frontend fetches author details separately

## Running Tools

### Python env

the venv of this project is at .venv sub-folder
or use `uv run python xxx` to run python scripts

### Full-Stack Web Application

Virtual environment is at .venv directory of the workspace
usually you don't need to start development server, if you have, ask to confirm
```bash
# Install dependencies and start development server
uv sync
uv run uvicorn backend.app.main:app --reload --port 8002

```

#### Technology Stack:
- **Backend**: FastAPI + SQLAlchemy + SQLite + JWT authentication
- **Frontend**: Vue 3 + TypeScript + Tailwind CSS 4 + Chart.js + Vite
- **Integration**: FastAPI serves Vue SPA with API routes prefixed with `/api/`

#### Features Available:
- **Authentication**: User registration and login with JWT tokens
- **Repository Management**: Add, view, analyze, and delete Git repositories  
- **Statistics Dashboard**: Interactive charts and visualizations of commit activity
- **Real-time Analysis**: Trigger Git analysis and view results immediately
- **Responsive Design**: Modern, clean UI that works on desktop and mobile

#### API Endpoints Available:

refer to docs/api-endpoints.md

## Development Guidelines

### Web Service Specific  
- Use FastAPI with SQLAlchemy for new API endpoints
- Follow day-based storage pattern - avoid storing aggregated or computed data
- Use migration system for all database schema changes
- Maintain user/author separation in data model
- Write Pydantic schemas for request/response validation
- Design APIs with date-indexed responses for frontend charting
- Return minimal data references (e.g. author_id) to avoid response bloat
- Support flexible filtering (repo scope, AI coder exclusion, date ranges)

### Database Migration Guides

refer to docs/database-migration-guides.md

## Documentation and Planning Requirements

### Mandatory Documentation for Major Changes
When implementing any significant module changes, feature additions, or architectural modifications, you MUST create and maintain documentation in the `docs/plan/` directory.

#### Required Documentation Process
1. **Create Planning Document**: Before starting any major modification, create a detailed plan document in `docs/plan/[feature-name]-plan.md`
2. **Document Progress**: Update the plan document with progress status as work progresses
3. **Maintain Both Tracking Systems**: Use both in-memory todo lists AND persistent documentation

#### Plan Document Structure
```markdown
# [Feature/Change Name] Plan

## Overview
Brief description of the change and its purpose

## Current Problem Analysis
Detailed analysis of what needs to be changed and why

## Strategy and Approach
How the change will be implemented

## Implementation Steps
Detailed breakdown of tasks with priorities and status

## Timeline
Expected completion dates for each phase

## Risk Assessment
Potential risks and mitigation strategies

## Success Criteria
How to measure successful completion

## Progress Tracking
Real-time status updates (✅ ✓ ⏳ ❌)

## Related Files
List of all files that will be modified
```

#### When to Create Plan Documents
- New feature implementations
- Architectural refactoring (like removing v1 dependencies)
- Database schema changes
- API version migrations
- Security enhancements
- Performance optimizations
- Major bug fixes that affect multiple components

#### Documentation Maintenance
- Update progress markers in real-time as tasks complete
- Record any deviation from original plan with reasoning
- Document lessons learned and implementation notes
- Keep status current for team visibility

This ensures that all major work is properly tracked, documented, and can be resumed by anyone on the team.