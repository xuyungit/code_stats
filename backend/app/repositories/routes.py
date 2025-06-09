import os
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.models import User, Repository, Author
from ..schemas.repositories import (
    RepositoryCreate, RepositoryUpdate, RepositoryResponse,
    AuthorResponse, AuthorUpdate
)
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/repositories", tags=["repositories"])


@router.get("/", response_model=List[RepositoryResponse])
async def list_repositories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all repositories for the current user."""
    repositories = db.query(Repository).filter(Repository.user_id == current_user.id).all()
    return repositories


@router.post("/", response_model=RepositoryResponse)
async def create_repository(
    repo_data: RepositoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new repository."""
    # Check if repository name already exists for this user
    existing = db.query(Repository).filter(
        Repository.user_id == current_user.id,
        Repository.name == repo_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository name already exists"
        )
    
    # Validate that the path exists and is a git repository
    if not os.path.isdir(repo_data.local_path):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository path does not exist"
        )
    
    if not os.path.isdir(os.path.join(repo_data.local_path, '.git')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Path is not a valid git repository"
        )
    
    # Create repository
    repository = Repository(
        user_id=current_user.id,
        name=repo_data.name,
        local_path=repo_data.local_path,
        description=repo_data.description
    )
    
    db.add(repository)
    db.commit()
    db.refresh(repository)
    
    return repository


@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific repository."""
    repository = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id
    ).first()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    return repository


@router.put("/{repo_id}", response_model=RepositoryResponse)
async def update_repository(
    repo_id: int,
    repo_data: RepositoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a repository."""
    repository = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id
    ).first()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    # Update fields
    update_data = repo_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(repository, field, value)
    
    db.commit()
    db.refresh(repository)
    
    return repository


@router.delete("/{repo_id}")
async def delete_repository(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a repository."""
    repository = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id
    ).first()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    db.delete(repository)
    db.commit()
    
    return {"message": "Repository deleted successfully"}


@router.get("/{repo_id}/authors", response_model=List[AuthorResponse])
async def list_repository_authors(
    repo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all authors for a repository."""
    # Verify repository ownership
    repository = db.query(Repository).filter(
        Repository.id == repo_id,
        Repository.user_id == current_user.id
    ).first()
    
    if not repository:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Repository not found"
        )
    
    # Get unique authors for this repository
    authors = db.query(Author).join(
        repository.daily_stats
    ).filter(
        repository.daily_stats.c.repository_id == repo_id
    ).distinct().all()
    
    return authors


@router.put("/authors/{author_id}", response_model=AuthorResponse)
async def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update author information (e.g., mark as AI coder)."""
    author = db.query(Author).filter(Author.id == author_id).first()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    # Update author
    author.is_ai_coder = author_data.is_ai_coder
    db.commit()
    db.refresh(author)
    
    return author