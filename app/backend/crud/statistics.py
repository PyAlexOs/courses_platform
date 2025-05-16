from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_, or_, case

from app.models.course import Course, Enrollment, Answer, Comment
from app.models.user import User
from app.schemas.statistics import CourseStatistics


class CRUDStatistics:
    async def get_course_stats(self, db: AsyncSession, course_id: int) -> CourseStatistics:
        # Total students enrolled
        total_students = await self._count_enrollments(db, course_id)
        
        # Active students (last 30 days)
        active_students = await self._count_active_students(db, course_id)
        
        # Completion rate
        completion_rate = await self._calculate_completion_rate(db, course_id)
        
        # Average score
        avg_score = await self._calculate_avg_score(db, course_id)
        
        # Module completion stats
        module_stats = await self._get_module_stats(db, course_id)
        
        # Recent activity
        recent_activity = await self._get_recent_activity(db, course_id)
        
        return CourseStatistics(
            total_students=total_students,
            active_students=active_students,
            completion_rate=completion_rate,
            average_score=avg_score,
            module_stats=module_stats,
            recent_activity=recent_activity,
        )

    async def _count_enrollments(self, db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count(Enrollment.id))
            .filter(Enrollment.course_id == course_id)
        )
        return result.scalar()

    async def _count_active_students(self, db: AsyncSession, course_id: int) -> int:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await db.execute(
            select(func.count(func.distinct(Answer.student_id)))
            .join(Answer.task)
            .join(Task.lesson)
            .join(Lesson.module)
            .join(Module.course)
            .filter(
                and_(
                    Course.id == course_id,
                    Answer.created_at >= thirty_days_ago
                )
            )
        )
        return result.scalar()

    async def _calculate_completion_rate(self, db: AsyncSession, course_id: int) -> float:
        result = await db.execute(
            select(func.avg(Enrollment.progress))
            .filter(Enrollment.course_id == course_id)
        )
        return result.scalar() or 0.0

    async def _calculate_avg_score(self, db: AsyncSession, course_id: int) -> float:
        result = await db.execute(
            select(func.avg(Answer.score))
            .join(Answer.task)
            .join(Task.lesson)
            .join(Lesson.module)
            .join(Module.course)
            .filter(Course.id == course_id)
        )
        return result.scalar() or 0.0

    async def _get_module_stats(self, db: AsyncSession, course_id: int) -> List[Dict[str, Any]]:
        result = await db.execute(
            select(
                Module.id,
                Module.title,
                func.count(func.distinct(Enrollment.user_id)).label("total_students"),
                func.avg(
                    case(
                        (and_(
                            Enrollment.progress >= 80,
                            Enrollment.course_id == course_id
                        ), 1),
                        else_=0
                    )
                ).label("completion_rate")
            )
            .join(Module.course)
            .join(Enrollment, Enrollment.course_id == Course.id)
            .filter(Course.id == course_id)
            .group_by(Module.id, Module.title)
        )
        return [dict(row) for row in result.all()]

    async def _get_recent_activity(self, db: AsyncSession, course_id: int) -> Dict[str, Any]:
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        # Answers submitted
        answers_result = await db.execute(
            select(func.count(Answer.id))
            .join(Answer.task)
            .join(Task.lesson)
            .join(Lesson.module)
            .join(Module.course)
            .filter(
                and_(
                    Course.id == course_id,
                    Answer.created_at >= seven_days_ago
                )
            )
        )
        answers = answers_result.scalar()
        
        # Comments posted
        comments_result = await db.execute(
            select(func.count(Comment.id))
            .join(Comment.material)
            .join(LessonMaterial.lesson)
            .join(Lesson.module)
            .join(Module.course)
            .filter(
                and_(
                    Course.id == course_id,
                    Comment.created_at >= seven_days_ago
                )
            )
        )
        comments = comments_result.scalar()
        
        return {
            "answers_submitted": answers,
            "comments_posted": comments,
            "period": "7 days"
        }

    async def get_system_stats(self, db: AsyncSession) -> Dict[str, Any]:
        # Total users
        total_users = await self._count_total_users(db)
        
        # Active users (last 30 days)
        active_users = await self._count_active_users(db)
        
        # Total courses
        total_courses = await self._count_total_courses(db)
        
        # Active courses (with activity last 30 days)
        active_courses = await self._count_active_courses(db)
        
        # Certificates issued
        certificates = await self._count_certificates(db)
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_courses": total_courses,
            "active_courses": active_courses,
            "certificates_issued": certificates,
        }

    async def _count_total_users(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(User.id)))
        return result.scalar()

    async def _count_active_users(self, db: AsyncSession) -> int:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await db.execute(
            select(func.count(func.distinct(Answer.student_id)))
            .filter(Answer.created_at >= thirty_days_ago)
        )
        return result.scalar()

    async def _count_total_courses(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Course.id)))
        return result.scalar()

    async def _count_active_courses(self, db: AsyncSession) -> int:
        thirty_days_ago = datetime.now() - timedelta(days=30)
        result = await db.execute(
            select(func.count(func.distinct(Module.course_id)))
            .join(Answer.task)
            .join(Task.lesson)
            .join(Lesson.module)
            .filter(Answer.created_at >= thirty_days_ago)
        )
        return result.scalar()

    async def _count_certificates(self, db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Certificate.id)))
        return result.scalar()


statistics = CRUDStatistics()