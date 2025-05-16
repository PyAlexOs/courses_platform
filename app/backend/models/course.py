from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    image_path = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    creator_id = Column(Integer, ForeignKey("users.id"))
    
    creator = relationship("User", back_populates="courses_created")
    modules = relationship("Module", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    teachers = relationship("CourseTeacher", back_populates="course", cascade="all, delete-orphan")


class CourseTeacher(Base):
    __tablename__ = "course_teachers"
    
    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"))
    teacher_id = Column(Integer, ForeignKey("users.id"))
    
    course = relationship("Course", back_populates="teachers")
    teacher = relationship("User", back_populates="teacher_courses")


class Module(Base):
    __tablename__ = "modules"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    course_id = Column(Integer, ForeignKey("courses.id"))
    order = Column(Integer)
    
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String)
    module_id = Column(Integer, ForeignKey("modules.id"))
    order = Column(Integer)
    
    module = relationship("Module", back_populates="lessons")
    materials = relationship("LessonMaterial", back_populates="lesson", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lesson", cascade="all, delete-orphan")


class LessonMaterial(Base):
    __tablename__ = "lesson_materials"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    content = Column(String)
    material_type = Column(String)  # text, video, pdf, etc.
    file_path = Column(String)
    order = Column(Integer)
    
    lesson = relationship("Lesson", back_populates="materials")
    comments = relationship("Comment", back_populates="material", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    title = Column(String)
    description = Column(String)
    task_type = Column(String)  # test, text, file_upload
    max_score = Column(Float)
    order = Column(Integer)
    
    lesson = relationship("Lesson", back_populates="tasks")
    answers = relationship("Answer", back_populates="task", cascade="all, delete-orphan")


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"))
    student_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    file_path = Column(String)
    score = Column(Float)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    feedback = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    task = relationship("Task", back_populates="answers")
    student = relationship("User", back_populates="answers", foreign_keys=[student_id])
    teacher = relationship("User", foreign_keys=[teacher_id])


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    material_id = Column(Integer, ForeignKey("lesson_materials.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    reply_to_id = Column(Integer, ForeignKey("comments.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False)
    
    material = relationship("LessonMaterial", back_populates="comments")
    author = relationship("User", back_populates="comments")
    replies = relationship("Comment", remote_side=[id])


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    progress = Column(Float, default=0.0)
    
    student = relationship("User", back_populates="courses_enrolled")
    course = relationship("Course", back_populates="enrollments")


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(Integer, ForeignKey("courses.id"))
    file_path = Column(String)
    score = Column(Float)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="certificates")
    course = relationship("Course")