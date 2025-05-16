from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from pathlib import Path

from app.crud.enrollment import enrollment as crud_enrollment
from app.services import certificate_service, notification_service
from app.core.config import settings
from app.core.security import get_current_active_user
from app.crud.certificate import certificate as crud_certificate
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.certificate import CertificateOut

router = APIRouter()


@router.get("/", response_model=List[CertificateOut])
async def read_user_certificates(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await crud_certificate.get_by_user(db, user_id=current_user.id, skip=skip, limit=limit)


@router.get("/{certificate_id}", response_class=FileResponse)
async def download_certificate(
    certificate_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    certificate = await crud_certificate.get(db, id=certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if certificate.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    file_path = Path(certificate.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Certificate file not found")
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=f"certificate_{certificate.course.title.replace(' ', '_')}.pdf"
    )


@router.post("/courses/{course_id}/generate", response_model=CertificateOut)
async def generate_certificate(
    course_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Check if user is enrolled in the course
    enrollment = await crud_enrollment.get_by_user_and_course(db, user_id=current_user.id, course_id=course_id)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not enrolled in this course",
        )
    
    # Check if user already has a certificate
    existing_cert = await crud_certificate.get_by_user_and_course(db, user_id=current_user.id, course_id=course_id)
    if existing_cert:
        return existing_cert
    
    # Check if user has completed the course (80% score)
    if enrollment.progress < 80:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You need to complete at least 80% of the course to get a certificate",
        )
    
    # Generate certificate
    certificate_path = await certificate_service.generate_certificate(db, user=current_user, course=enrollment.course)
    
    # Send notification
    await notification_service.send_certificate_issued_notification(
        db=db,
        user_id=current_user.id,
        course_title=enrollment.course.title,
        course_id=course_id,
    )
    
    return await crud_certificate.get_by_user_and_course(db, user_id=current_user.id, course_id=course_id)