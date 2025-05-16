from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.security import get_current_active_user, get_current_active_teacher
from app.crud.comment import comment as crud_comment
from app.crud.course import course as crud_course
from app.db.dependencies import get_db
from app.models.user import User
from app.schemas.comment import CommentOut, CommentCreate, CommentUpdate

router = APIRouter()


@router.get("/materials/{material_id}/comments", response_model=List[CommentOut])
async def read_material_comments(
    material_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    return await crud_comment.get_by_material(db, material_id=material_id, skip=skip, limit=limit)


@router.post("/materials/{material_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
    material_id: int,
    comment_in: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    comment_in.material_id = material_id
    comment_in.author_id = current_user.id
    return await crud_comment.create(db, obj_in=comment_in)


@router.put("/comments/{comment_id}", response_model=CommentOut)
async def update_comment(
    comment_id: int,
    comment_in: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    db_comment = await crud_comment.get(db, id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only author or teacher/admin can update
    if (db_comment.author_id != current_user.id and 
        current_user.role not in ["teacher", "admin"]):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return await crud_comment.update(db, db_obj=db_comment, obj_in=comment_in)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    db_comment = await crud_comment.get(db, id=comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    if current_user.role == "admin":
        await crud_comment.remove(db, id=comment_id)
    return None

    # Teacher can only delete comments in their courses
    is_teacher = await crud_course.is_teacher_of_course(
        db, 
        user_id=current_user.id, 
        course_id=db_comment.material.lesson.module.course_id
    )
    if db_comment.author_id != current_user.id and not is_teacher and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    await crud_comment.remove(db, id=comment_id)
    return None