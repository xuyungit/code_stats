# Git Stats API Backend

A FastAPI-based web service for analyzing git repository statistics with multi-user support.

## Features

- **Multi-user support**: Users can register and manage their own repositories
- **Repository management**: Add, update, and delete git repositories
- **Author tracking**: Separate git authors from system users, with AI coder flagging
- **Day-based statistics**: Atomic storage of daily statistics per author per repository
- **Migration system**: Database schema versioning and migration support
- **JWT Authentication**: Secure API access with token-based authentication

## Quick Start

### 1. Install Dependencies

```bash
# Install dependencies using uv
uv sync
```

### 2. Environment Setup

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Run Database Migrations

```bash
python -c "from app.core.migration_manager import migration_manager; migration_manager.migrate_up()"
```

### 4. Start Development Server

```bash
# From workspace root
uv run uvicorn backend.app.main:app --reload --port 8002

# Or from backend directory
cd backend
uv run uvicorn app.main:app --reload --port 8002
```

The API will be available at `http://localhost:8002`

### 5. View API Documentation

- Swagger UI: `http://localhost:8002/docs`
- ReDoc: `http://localhost:8002/redoc`

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Repositories
- `GET /repositories/` - List user's repositories
- `POST /repositories/` - Add new repository
- `GET /repositories/{repo_id}` - Get repository details
- `PUT /repositories/{repo_id}` - Update repository
- `DELETE /repositories/{repo_id}` - Delete repository
- `GET /repositories/{repo_id}/authors` - List repository authors
- `PUT /authors/{author_id}` - Update author (mark as AI coder)

## Database Schema

The system uses a day-based atomic storage approach:

- **users**: System users who use the web interface
- **authors**: Git authors who commit code (separate from users)
- **repositories**: Git repositories managed by users
- **daily_author_stats**: Daily statistics per author per repository (atomic unit)
- **analysis_jobs**: Track analysis job status
- **schema_migrations**: Database migration tracking

## Migration System

The built-in migration system handles database schema changes:

```python
from app.core.migration_manager import migration_manager

# Apply all pending migrations
migration_manager.migrate_up()

# Rollback to specific version
migration_manager.migrate_down("001")

# Check migration status
status = migration_manager.get_migration_status()
```

## Development

### Adding New Migrations

1. Create a new file in `migrations/` folder:
   - Format: `{version}_{description}.sql`
   - Example: `002_add_computed_columns.sql`

2. Structure your migration file:
   ```sql
   -- UP
   ALTER TABLE authors ADD COLUMN avatar_url VARCHAR(255);
   
   -- DOWN
   ALTER TABLE authors DROP COLUMN avatar_url;
   ```

3. Apply the migration:
   ```bash
   python -c "from app.core.migration_manager import migration_manager; migration_manager.migrate_up()"
   ```

### Project Structure

```
backend/
├── app/
│   ├── auth/              # Authentication logic
│   ├── core/              # Database, config, models
│   ├── repositories/      # Repository management
│   ├── statistics/        # Git analysis logic
│   ├── schemas/           # Pydantic models
│   └── main.py           # FastAPI app setup
├── migrations/           # Database migrations
└── tests/               # Test files
```

## Configuration

Key environment variables:

- `DATABASE_URL`: Database connection string (default: SQLite)
- `SECRET_KEY`: JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time
- `DEBUG`: Enable debug mode

## Production Deployment

1. Set production environment variables
2. Use PostgreSQL instead of SQLite
3. Configure proper CORS origins
4. Use a production WSGI server (gunicorn)
5. Set up Redis for background tasks
6. Configure proper logging