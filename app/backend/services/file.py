import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from fastapi import UploadFile

from app.core.config import settings


class FileService:
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.allowed_extensions = {
            ".jpg", ".jpeg", ".png", ".gif",  # Images
            ".pdf", ".doc", ".docx", ".txt",  # Documents
            ".mp4", ".mov", ".avi",  # Videos
            ".mp3", ".wav",  # Audio
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB

    async def save_upload_file(
        self, upload_file: UploadFile, subdir: str = ""
    ) -> Tuple[Optional[str], Optional[str]]:
        # Validate file extension
        file_ext = os.path.splitext(upload_file.filename)[1].lower()
        if file_ext not in self.allowed_extensions:
            return None, "File type not allowed"
        
        # Validate file size
        if upload_file.size > self.max_file_size:
            return None, "File size exceeds maximum allowed size"
        
        # Create upload directory if not exists
        upload_path = self.upload_dir / subdir
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        file_uuid = str(uuid.uuid4())
        filename = f"{file_uuid}{file_ext}"
        file_path = upload_path / filename
        
        # Save file
        try:
            with file_path.open("wb") as buffer:
                content = await upload_file.read()
                buffer.write(content)
        except Exception:
            return None, "Failed to save file"
        
        return str(file_path.relative_to(self.upload_dir)), None

    def get_file_path(self, relative_path: str) -> Optional[Path]:
        file_path = self.upload_dir / relative_path
        if file_path.exists() and file_path.is_file():
            return file_path
        return None

    def delete_file(self, relative_path: str) -> bool:
        file_path = self.upload_dir / relative_path
        try:
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception:
            return False


file_service = FileService()