import os
import sqlite3
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models import SchemaMigration


@dataclass
class Migration:
    version: str
    description: str
    up_sql: str
    down_sql: str = ""


class MigrationManager:
    def __init__(self, migrations_dir: str = "migrations"):
        self.migrations_dir = Path(migrations_dir)
        self.ensure_migrations_table()
    
    def ensure_migrations_table(self):
        """Create migrations table if it doesn't exist."""
        from .models import Base
        Base.metadata.create_all(bind=engine)
    
    def get_applied_migrations(self) -> List[str]:
        """Get list of applied migration versions."""
        with SessionLocal() as session:
            migrations = session.query(SchemaMigration).order_by(SchemaMigration.version).all()
            return [m.version for m in migrations]
    
    def get_available_migrations(self) -> List[Migration]:
        """Load all migration files from disk."""
        migrations = []
        if not self.migrations_dir.exists():
            return migrations
            
        for file_path in sorted(self.migrations_dir.glob("*.sql")):
            migration = self.parse_migration_file(file_path)
            if migration:
                migrations.append(migration)
        return migrations
    
    def parse_migration_file(self, file_path: Path) -> Optional[Migration]:
        """Parse a migration file."""
        try:
            content = file_path.read_text()
            
            # Extract version from filename (e.g., "001_initial_schema.sql" -> "001")
            version = file_path.stem.split('_')[0]
            
            # Extract description from filename
            description = '_'.join(file_path.stem.split('_')[1:]).replace('_', ' ')
            
            # Split UP and DOWN sections
            sections = content.split('-- DOWN')
            up_sql = sections[0].replace('-- UP', '').strip()
            down_sql = sections[1].strip() if len(sections) > 1 else ""
            
            return Migration(version, description, up_sql, down_sql)
        except Exception as e:
            print(f"Error parsing migration file {file_path}: {e}")
            return None
    
    def migrate_up(self, target_version: Optional[str] = None):
        """Apply pending migrations."""
        applied = set(self.get_applied_migrations())
        available = self.get_available_migrations()
        
        pending = [m for m in available if m.version not in applied]
        if target_version:
            pending = [m for m in pending if m.version <= target_version]
        
        with SessionLocal() as session:
            for migration in pending:
                print(f"Applying migration {migration.version}: {migration.description}")
                
                try:
                    # Execute migration SQL
                    engine.execute(migration.up_sql)
                    
                    # Record migration
                    migration_record = SchemaMigration(
                        version=migration.version,
                        description=migration.description
                    )
                    session.add(migration_record)
                    session.commit()
                    
                    print(f"✓ Applied migration {migration.version}")
                except Exception as e:
                    print(f"✗ Failed to apply migration {migration.version}: {e}")
                    session.rollback()
                    raise
    
    def migrate_down(self, target_version: str):
        """Rollback migrations to target version."""
        applied = self.get_applied_migrations()
        available = {m.version: m for m in self.get_available_migrations()}
        
        to_rollback = [v for v in reversed(applied) if v > target_version]
        
        with SessionLocal() as session:
            for version in to_rollback:
                if version in available and available[version].down_sql:
                    print(f"Rolling back migration {version}")
                    try:
                        engine.execute(available[version].down_sql)
                        session.query(SchemaMigration).filter(
                            SchemaMigration.version == version
                        ).delete()
                        session.commit()
                        print(f"✓ Rolled back migration {version}")
                    except Exception as e:
                        print(f"✗ Failed to rollback migration {version}: {e}")
                        session.rollback()
                        raise
                else:
                    print(f"⚠️ No rollback SQL for migration {version}")
    
    def get_migration_status(self) -> Dict[str, str]:
        """Get status of all migrations."""
        applied = set(self.get_applied_migrations())
        available = self.get_available_migrations()
        
        status = {}
        for migration in available:
            status[migration.version] = {
                "description": migration.description,
                "applied": migration.version in applied
            }
        
        return status


# Global migration manager instance
migration_manager = MigrationManager()