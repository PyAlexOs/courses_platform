# app/api/v1/__init__.py
from fastapi import APIRouter

api_router = APIRouter()

# Импортируем все endpoint-ы
from app.api.v1.endpoints import auth, users, courses, tasks, comments, certificates, notifications, statistics