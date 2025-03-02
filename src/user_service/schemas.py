from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str
    phone: Optional[str]
    email: Optional[str]


class ProfileUpdate(BaseModel):
    user_id: int
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    avatar: Optional[str]
    updated_at: Optional[datetime]


class UserProfileUpdate(BaseModel):
    token: str
    phone: Optional[str]
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    bio: Optional[str]
    date_of_birth: Optional[datetime]
    avatar: Optional[str]
    updated_at: Optional[datetime]


class SessionResponse(BaseModel):
    token: str
    expires_at: datetime
