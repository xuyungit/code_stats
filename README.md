# Code Stats

## Overview

Code Stats is a full-stack web application for analyzing Git repository activity. Originally a command-line tool, it has evolved into a multi-user web service that provides detailed statistics about development activity including commits, lines of code changes, and author contributions over time.

The application features a modern Vue.js frontend with interactive charts and a FastAPI backend with JWT authentication and SQLite database storage.

## Features

### Web Application
- **Multi-User Support:** User registration and authentication with JWT tokens
- **Repository Management:** Add, analyze, and manage multiple Git repositories
- **Interactive Dashboard:** Visual charts showing development activity over time
- **Real-time Analysis:** Trigger Git analysis and view results immediately
- **Author Tracking:** Separate tracking of Git authors vs system users
- **Responsive Design:** Modern UI that works on desktop and mobile

### Analysis Capabilities
- **Daily Statistics:** Day-by-day breakdown of Git activity
- **Period Analysis:** Configurable time ranges (7, 14, 30, 90 days)
- **Detailed Metrics:** For each period, shows:
  - Number of commits
  - Number of files changed  
  - Number of lines added/deleted
  - Net line changes
  - Author contributions
- **Manual AI Coder Flagging:** Mark authors as AI-generated code contributors

## Technology Stack

- **Backend:** FastAPI + SQLAlchemy + SQLite + JWT authentication
- **Frontend:** Vue 3 + TypeScript + Tailwind CSS + Chart.js + Vite
- **Package Management:** uv for Python, npm for Node.js
- **Database:** SQLite (development) with migration path to PostgreSQL

## Requirements

- Python 3.13+
- Node.js 18+ and npm
- Git installed and accessible in your system's PATH
- uv package manager for Python dependencies

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd code_stats

# Install Python dependencies
uv sync

# Install frontend dependencies
cd frontend
npm install
cd ..
```

## Usage

### Development Environment

Choose one of these approaches for frontend development:

#### Option 1: Separate Development Servers (Recommended for active frontend development)

```bash
# Terminal 1: Start backend server
uv run uvicorn backend.app.main:app --reload --port 8002

# Terminal 2: Start frontend development server with hot-reload
cd frontend
npm run dev
```

- Frontend with hot-reload: `http://localhost:5173`
- Backend API: `http://localhost:8002`
- API docs: `http://localhost:8002/api/docs`

**Note:** This requires proxy configuration in `vite.config.ts` to forward API calls from port 5173 to 8002.

#### Option 2: Integrated Serving (Current setup)

```bash
# Build frontend for production
cd frontend
npm run build
cd ..

# Start backend (serves built frontend)
uv run uvicorn backend.app.main:app --reload --port 8002
```

- Full application: `http://localhost:8002`
- API docs: `http://localhost:8002/api/docs`

### Production Environment

```bash
# Build optimized frontend
cd frontend
npm run build
cd ..

# Start production server
uv run uvicorn backend.app.main:app --host 0.0.0.0 --port 8002
```

### Legacy CLI Tool

The original command-line interface is still available:

```bash
python git_stats.py <repo_path> [--days N]
```

Example:
```bash
python git_stats.py /path/to/your/repo --days 30
```

## Testing

Run the full-stack integration test to verify everything is working:

```bash
# Start the server first
uv run uvicorn backend.app.main:app --reload --port 8002

# In another terminal, run the test
python test_fullstack.py
```

The test covers:
- API health checks and frontend serving
- User registration and authentication  
- Repository CRUD operations
- Git analysis triggering and completion
- Statistics retrieval and validation

## Architecture

### Backend (FastAPI)
- **Models**: SQLAlchemy models for Users, Repositories, Authors, and DailyAuthorStats
- **Authentication**: JWT-based user authentication and authorization
- **API Routes**: RESTful endpoints for all operations
- **Git Analysis**: Integrates existing CLI analysis logic with web service
- **Database**: Day-based atomic storage with calculated aggregations

### Frontend (Vue 3)
- **Authentication**: Login/register forms with JWT token management
- **Dashboard**: Overview with repository stats and quick actions
- **Repository Management**: CRUD interface for Git repositories
- **Statistics Visualization**: Interactive charts using Chart.js
- **Responsive Design**: Tailwind CSS for modern, mobile-friendly UI

### Data Model
- **Day-based Storage**: Only daily author statistics are stored in the database
- **Calculated Aggregations**: All period and summary statistics are computed from daily data
- **User/Author Separation**: System users are separate from Git commit authors
- **Manual AI Flagging**: Authors can be manually marked as AI-generated code

## API Documentation

When the server is running, visit `http://localhost:8002/api/docs` for interactive API documentation with Swagger UI.

## Development Notes

- The original CLI tool (`git_stats.py`) remains functional for backwards compatibility
- The web service adapts the existing Git analysis logic for multi-user database storage
- Frontend build artifacts are served directly by FastAPI for simple deployment
- Database migrations are handled automatically on server startup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the integration test to ensure everything works
5. Submit a pull request

## License

This project is open-source. Please add a specific license file if desired (e.g., MIT, Apache 2.0).
