from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any

from app.core.security import get_current_active_teacher, get_current_active_admin
from app.crud.course import course as crud_course
from app.crud.statistics import statistics as crud_statistics
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.statistics import CourseStatistics

router = APIRouter()


@router.get("/courses/{course_id}", response_model=CourseStatistics)
async def get_course_statistics(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    # Verify the teacher is assigned to this course
    is_teacher = await crud_course.is_teacher_of_course(
        db, 
        user_id=current_user.id, 
        course_id=course_id
    )
    if not is_teacher and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await crud_statistics.get_course_stats(db, course_id=course_id)


@router.get("/courses/{course_id}/progress", response_model=Dict[str, Any])
async def get_course_progress(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    is_teacher = await crud_course.is_teacher_of_course(
        db, 
        user_id=current_user.id, 
        course_id=course_id
    )
    if not is_teacher and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await crud_statistics.get_course_progress(db, course_id=course_id)


@router.get("/courses/{course_id}/activity", response_model=Dict[str, Any])
async def get_course_activity(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    is_teacher = await crud_course.is_teacher_of_course(
        db, 
        user_id=current_user.id, 
        course_id=course_id
    )
    if not is_teacher and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await crud_statistics.get_course_activity(db, course_id=course_id)


@router.get("/system/overview", response_model=Dict[str, Any])
async def get_system_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    return await crud_statistics.get_system_stats(db)