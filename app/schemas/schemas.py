from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Image Schemas
class ImageBase(BaseModel):
    warehouse_location: str

class ImageCreate(ImageBase):
    category_name: str
    tags: List[str] = []

class ImageResponse(BaseModel):
    id: int
    filename: str
    s3_url: str
    warehouse_location: str
    upload_date: datetime
    category_name: str
    tags: List[str] = []
    model_config = ConfigDict(from_attributes=True)
