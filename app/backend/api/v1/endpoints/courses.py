from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.schemas.course import CourseOut
from app.core.security import get_current_active_user, get_current_active_teacher, get_current_active_admin
from app.crud.course import course, module, lesson, material, task
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.course import (
    CourseCreate, CourseUpdate, CourseOut,
    ModuleCreate, ModuleUpdate, ModuleOut,
    LessonCreate, LessonUpdate, LessonOut,
    MaterialCreate, MaterialUpdate, MaterialOut,
    TaskCreate, TaskUpdate, TaskOut
)

router = APIRouter()


@router.get("/", response_model=List[CourseOut])
async def read_courses(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    courses = await course.get_multi_with_creator(db, skip=skip, limit=limit)
    return courses


@router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_in: CourseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    course_in.creator_id = current_user.id
    return await course.create(db, obj_in=course_in)


@router.get("/{course_id}", response_model=CourseOut)
async def read_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_course = await course.get_with_details(db, id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    return db_course


@router.put("/{course_id}", response_model=CourseOut)
async def update_course(
    course_id: int,
    course_in: CourseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    db_course = await course.get(db, id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await course.update(db, db_obj=db_course, obj_in=course_in)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    db_course = await course.get(db, id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    await course.remove(db, id=course_id)
    return None


# Modules endpoints
@router.post("/{course_id}/modules", response_model=ModuleOut, status_code=status.HTTP_201_CREATED)
async def create_module(
    course_id: int,
    module_in: ModuleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    # Check if user is course creator or admin
    db_course = await course.get(db, id=course_id)
    if not db_course:
        raise HTTPException(status_code=404, detail="Course not found")
    if db_course.creator_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    module_in.course_id = course_id
    return await module.create(db, obj_in=module_in)


# Similar endpoints for lessons, materials, tasks would follow...