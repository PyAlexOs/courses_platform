from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_password_hash, verify_password
from app.crud.user import user as crud_user
from app.db.dependencies import get_db
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserInDB, UserOut

router = APIRouter()


@router.post("/register", response_model=UserOut)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    # Check if user already exists
    existing_user = await crud_user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists.",
        )
    
    # Hash password
    hashed_password = get_password_hash(user_in.password)
    user_in_db = UserInDB(**user_in.dict(), password_hash=hashed_password)
    
    # Create user
    user = await crud_user.create(db, obj_in=user_in_db)
    return user


@router.post("/login", response_model=Token)
async def login(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = await crud_user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    access_token = create_access_token(subject=str(user.id))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/password-recovery/{email}")
async def recover_password(email: str, db: AsyncSession = Depends(get_db)):
    # TODO: Implement password recovery logic
    return {"message": "Password recovery email sent"}