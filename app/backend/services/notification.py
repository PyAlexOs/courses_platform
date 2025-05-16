from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.notification import notification as crud_notification
from app.models.user import User
from app.schemas.notification import NotificationCreate


async def create_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    message: str,
    notification_type: str,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
) -> None:
    notification_in = NotificationCreate(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=notification_type,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        is_read=False,
    )
    await crud_notification.create(db, obj_in=notification_in)


async def send_comment_reply_notification(
    db: AsyncSession,
    comment_author_id: int,
    reply_author: User,
    material_id: int,
    course_id: int,
) -> None:
    if comment_author_id == reply_author.id:
        return  # Don't notify about self-replies
    
    await create_notification(
        db=db,
        user_id=comment_author_id,
        title="Новый ответ на ваш комментарий",
        message=f"{reply_author.first_name} ответил(а) на ваш комментарий",
        notification_type="comment_reply",
        related_entity_type="course",
        related_entity_id=course_id,
    )


async def send_assignment_graded_notification(
    db: AsyncSession,
    student_id: int,
    teacher: User,
    task_id: int,
    course_id: int,
    score: float,
) -> None:
    await create_notification(
        db=db,
        user_id=student_id,
        title="Ваше задание проверено",
        message=f"{teacher.first_name} оценил(а) ваше задание на {score} баллов",
        notification_type="assignment_graded",
        related_entity_type="course",
        related_entity_id=course_id,
    )


async def send_certificate_issued_notification(
    db: AsyncSession,
    user_id: int,
    course_title: str,
    course_id: int,
) -> None:
    await create_notification(
        db=db,
        user_id=user_id,
        title="Сертификат выдан",
        message=f"Вы получили сертификат за курс '{course_title}'",
        notification_type="certificate_issued",
        related_entity_type="course",
        related_entity_id=course_id,
    )


async def send_system_notification(
    db: AsyncSession,
    user_id: int,
    title: str,
    message: str,
) -> None:
    await create_notification(
        db=db,
        user_id=user_id,
        title=title,
        message=message,
        notification_type="system",
    )