# API Endpoints Available:

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