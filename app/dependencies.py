# app/dependencies.py

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection

from app.config import SECRET_KEY, ALGORITHM, DATABASE_URL, DATABASE_NAME
from app.crud import get_user_by_email
from app.schemas import TokenDataSchema, UserResponseSchema, UserInDB

# Setup OAuth2 password bearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_token(token: str, credentials_exception) -> TokenDataSchema:
    """Verify JWT token and return token data."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenDataSchema(email=email)
    except JWTError:
        raise credentials_exception
    return token_data


async def get_db() -> AsyncIOMotorDatabase:
    """Get the database instance."""
    client = AsyncIOMotorClient(DATABASE_URL)
    return client[DATABASE_NAME]


async def get_user_collection(db: AsyncIOMotorDatabase = Depends(get_db)) -> AsyncIOMotorCollection:
    """Get the users collection from the database."""
    return db["users"]


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncIOMotorCollection = Depends(get_user_collection)) -> UserResponseSchema:
    """Get the current user from the database using the provided token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user: UserInDB = await get_user_by_email(db, token_data.email)
    if user is None:
        raise credentials_exception
    return UserResponseSchema(**user.model_dump())
