from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.course import course as crud_course
from app.crud.enrollment import enrollment as crud_enrollment
from app.crud.task import task as crud_task
from app.crud.answer import answer as crud_answer
from app.models.course import Course
from app.models.user import User


class CourseService:
    async def enroll_user(
        self,
        db: AsyncSession,
        user: User,
        course_id: int,
    ) -> bool:
        # Check if user is already enrolled
        existing_enrollment = await crud_enrollment.get_by_user_and_course(
            db, user_id=user.id, course_id=course_id
        )
        if existing_enrollment:
            return False
        
        # Create enrollment
        await crud_enrollment.create(db, obj_in={
            "user_id": user.id,
            "course_id": course_id,
        })
        return True

    async def get_course_with_progress(
        self,
        db: AsyncSession,
        course_id: int,
        user_id: int,
    ) -> Optional[Course]:
        course = await crud_course.get_with_details(db, id=course_id)
        if not course:
            return None
        
        # Get user's progress
        enrollment = await crud_enrollment.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        if enrollment:
            course.user_progress = enrollment.progress
        
        return course

    async def calculate_course_progress(
        self,
        db: AsyncSession,
        user_id: int,
        course_id: int,
    ) -> float:
        # Get all tasks in course
        tasks = await crud_task.get_by_course(db, course_id=course_id)
        if not tasks:
            return 0.0
        
        # Get user's answers
        answers = await crud_answer.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        
        # Calculate progress
        total_score = sum(task.max_score for task in tasks)
        if total_score == 0:
            return 0.0
        
        user_score = sum(answer.score for answer in answers if answer.score is not None)
        progress = (user_score / total_score) * 100
        
        # Update enrollment
        enrollment = await crud_enrollment.get_by_user_and_course(
            db, user_id=user_id, course_id=course_id
        )
        if enrollment:
            await crud_enrollment.update(
                db, db_obj=enrollment, obj_in={"progress": progress}
            )
        
        return progress