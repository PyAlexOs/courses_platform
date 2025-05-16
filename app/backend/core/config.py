from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Online Courses Platform"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_EXTENSIONS: str = ".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx,.txt,.mp4,.mov,.avi,.mp3,.wav"
    
    # Backup settings
    BACKUP_DIR: str = "backups"
    
    # Maintenance mode
    MAINTENANCE_MODE: bool = False
    
    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
