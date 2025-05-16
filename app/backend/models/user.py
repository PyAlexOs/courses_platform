from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from app.models.base import Base


class UserRole(str, PyEnum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    middle_name = Column(String)
    phone = Column(String)
    profile_description = Column(String)
    gender = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    profile_image_path = Column(String)
    
    courses_created = relationship("Course", back_populates="creator")
    courses_enrolled = relationship("Enrollment", back_populates="student")
    comments = relationship("Comment", back_populates="author")
    answers = relationship("Answer", back_populates="student")
    certificates = relationship("Certificate", back_populates="user")
    
    teacher_courses = relationship("CourseTeacher", back_populates="teacher")


class TeacherProfile(Base):
    __tablename__ = "teacher_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    specialization = Column(String)
    experience = Column(String)
    bio = Column(String)
    
    user = relationship("User", backref="teacher_profile")