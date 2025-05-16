from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.services import statistics_service, admin_service
from app.core.security import get_current_active_admin
from app.crud.user import user as crud_user
from app.crud.course import course as crud_course
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.admin import (
    SystemStats,
    UserActivityReport,
    CourseReport,
    BackupRequest,
    BackupResponse,
)

router = APIRouter()


@router.get("/stats", response_model=SystemStats)
async def get_system_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    return await statistics_service.get_system_stats(db)


@router.get("/users/activity", response_model=List[UserActivityReport])
async def get_user_activity_report(
    days: int = 30,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    return await statistics_service.get_user_activity_report(db, days=days)


@router.get("/courses/report", response_model=List[CourseReport])
async def get_courses_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    return await statistics_service.get_courses_report(db)


@router.post("/backup", response_model=BackupResponse)
async def create_backup(
    backup_request: BackupRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    backup_path = await admin_service.create_backup(
        db,
        include_data=backup_request.include_data,
        include_files=backup_request.include_files,
    )
    return {"backup_path": backup_path}


@router.post("/restore", status_code=status.HTTP_204_NO_CONTENT)
async def restore_backup(
    backup_path: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    success = await admin_service.restore_backup(db, backup_path=backup_path)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to restore backup",
        )
    return None


@router.post("/maintenance/enable", status_code=status.HTTP_204_NO_CONTENT)
async def enable_maintenance_mode(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    await admin_service.set_maintenance_mode(db, enabled=True)
    return None


@router.post("/maintenance/disable", status_code=status.HTTP_204_NO_CONTENT)
async def disable_maintenance_mode(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_admin),
):
    await admin_service.set_maintenance_mode(db, enabled=False)
    return None