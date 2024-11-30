from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    name: str = Field(..., max_length=50, example="John Doe")
    email: EmailStr = Field(..., example="example@example.com")
    bio: Optional[str] = Field("", max_length=200, example="This is a bio.")
    following: List[str] = Field(default_factory=list)


class UserUpdate(UserCreate):
    pass


class Comment(BaseModel):
    comment_id: str = Field(..., example="unique_comment_id_123")
    user_id: str = Field(..., example="unique_user_id_123")
    content: str = Field(..., max_length=500, example="This is a comment.")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class PostCreate(BaseModel):
    post_id: str = Field(..., example="unique_post_id_123")
    user_id: str = Field(..., example="unique_user_id_123")
    content: str = Field(..., max_length=1000, example="This is the content of the post.")
    likes: List[str] = Field(default_factory=list)
    comments: List[Comment] = Field(default_factory=list)
