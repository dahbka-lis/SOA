from pydantic import BaseModel
from datetime import datetime
from typing import List


class PostBase(BaseModel):
    title: str
    description: str
    is_private: bool = False
    tags: List[str] = []


class PostCreate(PostBase):
    creator_id: str


class PostUpdate(PostBase):
    pass


class PostOut(PostBase):
    id: int
    creator_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class CommentOut(BaseModel):
    id: int
    post_id: int
    content: str
    creator_id: str
    created_at: datetime

    class Config:
        orm_mode = True
