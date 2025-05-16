from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from app.crud.base import CRUDBase
from app.models.course import Course, Module, Lesson, LessonMaterial, Task
from app.schemas.course import CourseCreate, CourseUpdate, ModuleCreate, ModuleUpdate, LessonCreate, LessonUpdate


class CRUDCourse(CRUDBase[Course, CourseCreate, CourseUpdate]):
    async def get_multi_with_creator(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[Course]:
        result = await db.execute(
            select(self.model)
            .options(joinedload(self.model.creator))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().unique().all()

    async def get_with_details(self, db: AsyncSession, id: int) -> Optional[Course]:
        result = await db.execute(
            select(self.model)
            .options(
                joinedload(self.model.creator),
                joinedload(self.model.modules)
                .joinedload(Module.lessons)
                .joinedload(Lesson.materials),
                joinedload(self.model.modules)
                .joinedload(Module.lessons)
                .joinedload(Lesson.tasks),
                joinedload(self.model.teachers)
                .joinedload(CourseTeacher.teacher),
            )
            .filter(self.model.id == id)
        )
        return result.scalars().unique().first()


class CRUDModule(CRUDBase[Module, ModuleCreate, ModuleUpdate]):
    async def get_by_course(self, db: AsyncSession, course_id: int) -> List[Module]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.course_id == course_id)
            .order_by(self.model.order)
        )
        return result.scalars().all()


class CRUDLesson(CRUDBase[Lesson, LessonCreate, LessonUpdate]):
    async def get_by_module(self, db: AsyncSession, module_id: int) -> List[Lesson]:
        result = await db.execute(
            select(self.model)
            .filter(self.model.module_id == module_id)
            .order_by(self.model.order)
        )
        return result.scalars().all()


class CRUDMaterial(CRUDBase[LessonMaterial, LessonMaterialCreate, LessonMaterialUpdate]):
    pass


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    pass


course = CRUDCourse(Course)
module = CRUDModule(Module)
lesson = CRUDLesson(Lesson)
material = CRUDMaterial(LessonMaterial)
task = CRUDTask(Task)