from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.security import get_current_active_user, get_current_active_teacher
from app.db.dependencies import get_db
from app.models.user import User
from app.services.file import file_service

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    subdir: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    file_path, error = await file_service.save_upload_file(file, subdir=subdir)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return {"file_path": file_path}


@router.get("/download/{file_path:path}")
async def download_file(
    file_path: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    full_path = file_service.get_file_path(file_path)
    if not full_path:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        full_path,
        filename=full_path.name,
    )


@router.delete("/{file_path:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(
    file_path: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_teacher),
):
    if not file_service.delete_file(file_path):
        raise HTTPException(status_code=404, detail="File not found or already deleted")
    return None