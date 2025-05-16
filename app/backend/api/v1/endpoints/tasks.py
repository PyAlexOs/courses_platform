from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.crud.course import course as crud_course
from app.core.security import get_current_active_user, get_current_active_teacher
from app.crud.task import task as crud_task
from app.crud.answer import answer as crud_answer
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.task import TaskOut, TaskCreate, TaskUpdate
from app.schemas.answer import AnswerOut, AnswerCreate, AnswerUpdate, AnswerGrade

router = APIRouter()


@router.get("/tasks/{task_id}", response_model=TaskOut)
async def read_task(
    task_id: int,
    db: AsyncSession = Depends(get_db),
):
    db_task = await crud_task.get_with_lesson(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task


@router.post("/tasks/{task_id}/answers", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
async def create_answer(
    task_id: int,
    answer_in: AnswerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verify task exists
    db_task = await crud_task.get(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # For test tasks, automatically check if correct
    if db_task.task_type == "test":
        is_correct = answer_in.content == db_task.correct_answer
        answer_in.score = db_task.max_score if is_correct else 0
        answer_in.is_correct = is_correct
    
    answer_in.task_id = task_id
    answer_in.student_id = current_user.id
    return await crud_answer.create(db, obj_in=answer_in)


@router.post("/tasks/{task_id}/answers/upload", response_model=AnswerOut, status_code=status.HTTP_201_CREATED)
async def upload_answer_file(
    task_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Verify task exists and accepts file uploads
    db_task = await crud_task.get(db, id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.task_type != "file_upload":
        raise HTTPException(status_code=400, detail="This task doesn't accept file uploads")
    
    # Save file
    file_path = f"uploads/answers/{task_id}_{current_user.id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    # Create answer record
    answer_in = AnswerCreate(
        task_id=task_id,
        student_id=current_user.id,
        file_path=file_path,
    )
    return await crud_answer.create(db, obj_in=answer_in)


@router.get("/answers/{answer_id}", response_model=AnswerOut)
async def read_answer(
    answer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_answer = await crud_answer.get_with_details(db, id=answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Only student, teacher or admin can view answer
    if (db_answer.student_id != current_user.id and 
        current_user.role not in ["teacher", "admin"]):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return db_answer


@router.put("/answers/{answer_id}/grade", response_model=AnswerOut)
async def grade_answer(
    answer_id: int,
    grade: AnswerGrade,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    db_answer = await crud_answer.get(db, id=answer_id)
    if not db_answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    
    # Verify the teacher is assigned to this course
    is_teacher = await crud_course.is_teacher_of_course(
        db, 
        user_id=current_user.id, 
        course_id=db_answer.task.lesson.module.course_id
    )
    if not is_teacher and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    update_data = {
        "score": grade.score,
        "teacher_id": current_user.id,
        "feedback": grade.feedback,
    }
    return await crud_answer.update(db, db_obj=db_answer, obj_in=update_data)