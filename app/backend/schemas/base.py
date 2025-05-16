from datetime import datetime
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, EmailStr
from pydantic.generics import GenericModel


T = TypeVar('T')


class ResponseSchema(BaseModel):
    message: str
    data: Optional[T] = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    items: list[T]
