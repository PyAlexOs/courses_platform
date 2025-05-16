from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.crud.certificate import certificate as crud_certificate
from app.crud.enrollment import enrollment as crud_enrollment
from app.models.course import Course
from app.models.user import User
from app.utils import generate_pdf_certificate


async def check_and_generate_certificate(
    db: AsyncSession,
    user: User,
    course: Course,
) -> Optional[str]:
    # Check if certificate already exists
    existing_cert = await crud_certificate.get_by_user_and_course(db, user_id=user.id, course_id=course.id)
    if existing_cert:
        return existing_cert.file_path
    
    # Check if user has completed the course (80% score)
    enrollment = await crud_enrollment.get_by_user_and_course(db, user_id=user.id, course_id=course.id)
    if not enrollment or enrollment.progress < 80:
        return None
    
    # Generate certificate
    cert_data = {
        "student_name": f"{user.last_name} {user.first_name}",
        "course_title": course.title,
        "completion_date": datetime.now().strftime("%d.%m.%Y"),
        "score": f"{enrollment.progress:.0f}%",
    }
    
    # Ensure certificates directory exists
    cert_dir = Path(settings.CERTIFICATES_DIR)
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"certificate_{user.id}_{course.id}.pdf"
    filepath = str(cert_dir / filename)
    
    generate_pdf_certificate(cert_data, filepath)
    
    # Save certificate record to DB
    await crud_certificate.create(db, obj_in={
        "user_id": user.id,
        "course_id": course.id,
        "file_path": filepath,
        "score": enrollment.progress,
    })
    
    return filepath