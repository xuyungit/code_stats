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

### Web Service Features (MVP Complete)
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

### Full-Stack Web Application

Virtual environment is at .venv directory of the workspace
```bash
# Install dependencies and start development server
uv sync
uv run uvicorn backend.app.main:app --reload --port 8002

# Access web application at http://localhost:8002
# API documentation at http://localhost:8002/api/docs
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

**Core & Health:**
- **GET** `/api/` - API info and version
- **GET** `/api/health` - Health check

**Authentication:**
- **POST** `/api/auth/register` - Register new user
- **POST** `/api/auth/login` - Login and get access token
- **GET** `/api/auth/me` - Get current user info
- **POST** `/api/auth/refresh` - Refresh access token

**Repository Management:**
- **GET** `/api/repositories/` - List user repositories
- **POST** `/api/repositories/` - Create repository
- **GET** `/api/repositories/{id}` - Get repository details
- **PUT** `/api/repositories/{id}` - Update repository
- **DELETE** `/api/repositories/{id}` - Delete repository
- **GET** `/api/repositories/{id}/authors` - List repository authors
- **PUT** `/api/repositories/authors/{author_id}` - Update author (AI flagging)

**Single-Repository Statistics:**
- **GET** `/api/repositories/{id}/stats/period` - Aggregated period stats
- **GET** `/api/repositories/{id}/stats/daily` - Daily breakdown stats
- **GET** `/api/repositories/{id}/stats/authors` - Author breakdown stats
- **GET** `/api/repositories/{id}/stats/daily-authors` - Daily stats with author details

**Analysis & Jobs:**
- **POST** `/api/repositories/{id}/analyze` - Trigger git analysis
- **GET** `/api/repositories/{id}/jobs` - List analysis jobs
- **GET** `/api/repositories/{id}/jobs/{job_id}` - Get job details

**Cross-Repository Statistics:**
- **GET** `/api/stats/repo-daily` - Multi-repo daily stats with author breakdown

## Development Guidelines

### Web Service Specific  
- Use FastAPI with SQLAlchemy for new API endpoints
- Follow day-based storage pattern - avoid storing aggregated or computed data
- Use migration system for all database schema changes
- Maintain user/author separation in data model
- Use JWT authentication for API security
- Write Pydantic schemas for request/response validation
- Design APIs with date-indexed responses for frontend charting
- Return minimal data references (e.g. author_id) to avoid response bloat
- Support flexible filtering (repo scope, AI coder exclusion, date ranges)

### Database Migrations
- Create migration files in `backend/migrations/` with format `{version}_{description}.sql`
- Include both UP and DOWN migration SQL
- Test migrations before applying to production
- Use migration manager for all schema changes