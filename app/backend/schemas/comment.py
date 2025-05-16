from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import ResponseSchema

class CommentBase(BaseModel):
    content: str = Field(..., max_length=1000)

class CommentCreate(CommentBase):
    material_id: int
    reply_to_id: Optional[int] = None

class CommentUpdate(BaseModel):
    content: Optional[str] = Field(None, max_length=1000)

class CommentInDB(CommentBase):
    id: int
    material_id: int
    author_id: int
    reply_to_id: Optional[int] = None
    is_deleted: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CommentWithReplies(CommentInDB):
    replies: List["CommentInDB"] = []

class CommentResponse(ResponseSchema):
    data: CommentInDB

# Решение проблемы циклических импортов
CommentWithReplies.update_forward_refs()