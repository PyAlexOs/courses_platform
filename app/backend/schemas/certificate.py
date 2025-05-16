from datetime import datetime
from pydantic import BaseModel
from app.schemas.base import ResponseSchema

class CertificateBase(BaseModel):
    user_id: int
    course_id: int
    score: float

class CertificateCreate(CertificateBase):
    pass

class CertificateInDB(CertificateBase):
    id: int
    file_path: str
    issued_at: datetime

    class Config:
        orm_mode = True

class CertificateResponse(ResponseSchema):
    data: CertificateInDB