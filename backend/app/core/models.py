from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    repositories = relationship("Repository", back_populates="owner")


class Author(Base):
    __tablename__ = "authors"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    is_ai_coder = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    daily_stats = relationship("DailyAuthorStats", back_populates="author")
    commits = relationship("Commit", back_populates="author")
    co_authored_commits = relationship("CommitCoAuthor", back_populates="author")


class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    local_path = Column(String(500), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    last_analyzed_at = Column(DateTime(timezone=True))
    
    # Relationships
    owner = relationship("User", back_populates="repositories")
    daily_stats = relationship("DailyAuthorStats", back_populates="repository")
    commits = relationship("Commit", back_populates="repository")
    analysis_jobs = relationship("AnalysisJob", back_populates="repository")


class DailyAuthorStats(Base):
    __tablename__ = "daily_author_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    date = Column(Date, nullable=False)
    commits_count = Column(Integer, default=0)
    added_lines = Column(Integer, default=0)
    deleted_lines = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="daily_stats")
    author = relationship("Author", back_populates="daily_stats")


class Commit(Base):
    __tablename__ = "commits"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    hash = Column(String(40), nullable=False, index=True)  # Git commit hash
    message = Column(Text, nullable=False)
    commit_datetime = Column(DateTime(timezone=True), nullable=False)
    added_lines = Column(Integer, default=0)
    deleted_lines = Column(Integer, default=0)
    files_changed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="commits")
    author = relationship("Author", back_populates="commits")
    co_authors = relationship("CommitCoAuthor", back_populates="commit")


class CommitCoAuthor(Base):
    __tablename__ = "commit_co_authors"
    
    id = Column(Integer, primary_key=True, index=True)
    commit_id = Column(Integer, ForeignKey("commits.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("authors.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    commit = relationship("Commit", back_populates="co_authors")
    author = relationship("Author", back_populates="co_authored_commits")


class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    job_type = Column(String(50), nullable=False)  # full_analysis, incremental, etc.
    date_from = Column(Date)
    date_to = Column(Date)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    records_processed = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    repository = relationship("Repository", back_populates="analysis_jobs")


class SchemaMigration(Base):
    __tablename__ = "schema_migrations"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    applied_at = Column(DateTime(timezone=True), server_default=func.now())