from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import get_current_active_user
from app.crud.notification import notification as crud_notification
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.notification import NotificationOut, NotificationUpdate

router = APIRouter()


@router.get("/", response_model=List[NotificationOut])
async def read_notifications(
    skip: int = 0,
    limit: int = 100,
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    if unread_only:
        return await crud_notification.get_unread_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return await crud_notification.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{notification_id}", response_model=NotificationOut)
async def read_notification(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = await crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return notification


@router.put("/{notification_id}", response_model=NotificationOut)
async def update_notification(
    notification_id: int,
    notification_in: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    notification = await crud_notification.get(db, id=notification_id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return await crud_notification.update(db, db_obj=notification, obj_in=notification_in)


@router.put("/mark-all-as-read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    await crud_notification.mark_all_as_read(db, user_id=current_user.id)
    return None


@router.get("/count/unread", response_model=int)
async def count_unread_notifications(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await crud_notification.count_unread_by_user(db, user_id=current_user.id)