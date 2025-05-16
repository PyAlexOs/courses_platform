import os
from pathlib import Path
from fastapi import UploadFile
from typing import Optional


async def save_upload_file(upload_file: UploadFile, destination: Path) -> Optional[str]:
    try:
        with destination.open("wb") as buffer:
            content = await upload_file.read()
            buffer.write(content)
        return str(destination)
    except Exception:
        return None


def ensure_directory_exists(path: str) -> bool:
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower()


def is_allowed_file_extension(filename: str, allowed_extensions: set) -> bool:
    return get_file_extension(filename) in allowed_extensions