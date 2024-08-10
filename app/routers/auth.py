# auth.py

from datetime import timedelta, datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from motor.motor_asyncio import AsyncIOMotorCollection

from app.config import SECRET_KEY, ALGORITHM
from app.crud import create_user, verify_user_password, get_user_by_email
from app.dependencies import get_user_collection, get_current_user
from app.schemas import UserCreateSchema, UserResponseSchema, TokenSchema

# Initialize the router
router = APIRouter()

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@router.post("/token", response_model=TokenSchema)
@router.post("/login", response_model=TokenSchema)
async def login_for_access_token(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncIOMotorCollection = Depends(get_user_collection)
) -> Any:
    user = await get_user_by_email(db, form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not await verify_user_password(db, user.email, form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/signup", response_model=UserResponseSchema)
async def register_user(
        user: UserCreateSchema,
        db: AsyncIOMotorCollection = Depends(get_user_collection)
) -> UserResponseSchema:
    db_user = await get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    new_user = await create_user(db, user)
    return new_user


@router.get("/users/me", response_model=UserResponseSchema)
async def read_users_me(current_user: UserResponseSchema = Depends(get_current_user)) -> UserResponseSchema:
    return current_user
