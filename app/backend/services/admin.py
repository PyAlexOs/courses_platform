import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import Base


class AdminService:
    async def create_backup(
        self,
        db: AsyncSession,
        include_data: bool = True,
        include_files: bool = True,
    ) -> str:
        # Create backup directory if not exists
        backup_dir = Path(settings.BACKUP_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"backup_{timestamp}"
        backup_path = backup_dir / backup_name
        backup_path.mkdir()
        
        # Backup database
        if include_data:
            db_backup_path = backup_path / "database.sql"
            db_url = str(db.bind.url)
            subprocess.run(
                [
                    "pg_dump",
                    "-Fc",
                    "-f", str(db_backup_path),
                    db_url,
                ],
                check=True,
            )
        
        # Backup files
        if include_files:
            files_backup_path = backup_path / "uploads"
            os.system(f"cp -r {settings.UPLOAD_DIR} {files_backup_path}")
        
        # Create archive
        archive_path = backup_dir / f"{backup_name}.tar.gz"
        subprocess.run(
            [
                "tar",
                "-czf",
                str(archive_path),
                "-C",
                str(backup_dir),
                backup_name,
            ],
            check=True,
        )
        
        # Cleanup
        subprocess.run(["rm", "-rf", str(backup_path)], check=True)
        
        return str(archive_path)

    async def restore_backup(self, db: AsyncSession, backup_path: str) -> bool:
        try:
            # Extract archive
            backup_dir = Path(backup_path).parent
            subprocess.run(
                [
                    "tar",
                    "-xzf",
                    backup_path,
                    "-C",
                    str(backup_dir),
                ],
                check=True,
            )
            
            # Restore database
            backup_name = Path(backup_path).stem
            extracted_dir = backup_dir / backup_name
            db_backup = extracted_dir / "database.sql"
            
            if db_backup.exists():
                db_url = str(db.bind.url)
                subprocess.run(
                    [
                        "pg_restore",
                        "-d", db_url,
                        "-c",  # Clean (drop) database objects before recreating
                        str(db_backup),
                    ],
                    check=True,
                )
            
            # Restore files
            files_backup = extracted_dir / "uploads"
            if files_backup.exists():
                subprocess.run(
                    [
                        "cp",
                        "-r",
                        str(files_backup),
                        settings.UPLOAD_DIR,
                    ],
                    check=True,
                )
            
            # Cleanup
            subprocess.run(["rm", "-rf", str(extracted_dir)], check=True)
            return True
        except Exception:
            return False

    async def set_maintenance_mode(self, db: AsyncSession, enabled: bool) -> None:
        # In a real application, this would set a flag in the database
        # or a configuration file that would be checked by a middleware
        pass


admin_service = AdminService()