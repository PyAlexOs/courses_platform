from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import ResponseSchema

class NotificationType(str, Enum):
    SYSTEM = "system"
    COURSE = "course"
    COMMENT = "comment"
    ASSIGNMENT = "assignment"
    CERTIFICATE = "certificate"

class NotificationBase(BaseModel):
    title: str = Field(..., max_length=100)
    message: str = Field(..., max_length=500)
    notification_type: NotificationType
    is_read: bool = False

class NotificationCreate(NotificationBase):
    user_id: int
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None

class NotificationUpdate(BaseModel):
    is_read: Optional[bool] = None

class NotificationInDB(NotificationBase):
    id: int
    user_id: int
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[int] = None
    created_at: datetime

    class Config:
        orm_mode = True

class NotificationResponse(ResponseSchema):
    data: NotificationInDB