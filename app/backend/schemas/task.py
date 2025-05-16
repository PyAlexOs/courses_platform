from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.base import ResponseSchema

class TaskType(str, Enum):
    TEST = "test"
    TEXT = "text"
    FILE_UPLOAD = "file_upload"

class TaskBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    task_type: TaskType
    max_score: float = Field(..., gt=0)
    order: int = Field(..., ge=0)

class TaskCreate(TaskBase):
    lesson_id: int
    correct_answer: Optional[str] = None  # Для тестовых заданий

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    max_score: Optional[float] = Field(None, gt=0)
    correct_answer: Optional[str] = None
    order: Optional[int] = Field(None, ge=0)

class TaskInDB(TaskBase):
    id: int
    lesson_id: int
    correct_answer: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True

class TaskWithAnswers(TaskInDB):
    answers: List["AnswerInDB"] = []

class AnswerBase(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = None

class AnswerCreate(AnswerBase):
    task_id: int

class AnswerUpdate(BaseModel):
    content: Optional[str] = None
    file_path: Optional[str] = None

class AnswerGrade(BaseModel):
    score: float = Field(..., ge=0)
    feedback: Optional[str] = None

class AnswerInDB(AnswerBase):
    id: int
    task_id: int
    student_id: int
    score: Optional[float] = None
    teacher_id: Optional[int] = None
    feedback: Optional[str] = None
    is_correct: Optional[bool] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AnswerResponse(ResponseSchema):
    data: AnswerInDB

# Решение проблемы циклических импортов
TaskWithAnswers.update_forward_refs()