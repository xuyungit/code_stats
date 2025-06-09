from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class RepositoryCreate(BaseModel):
    name: str
    local_path: str
    description: Optional[str] = None


class RepositoryUpdate(BaseModel):
    name: Optional[str] = None
    local_path: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RepositoryResponse(BaseModel):
    id: int
    name: str
    local_path: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_analyzed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AuthorResponse(BaseModel):
    id: int
    email: str
    name: str
    is_ai_coder: bool
    
    class Config:
        from_attributes = True


class AuthorUpdate(BaseModel):
    is_ai_coder: bool