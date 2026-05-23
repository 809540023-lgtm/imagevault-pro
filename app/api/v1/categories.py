from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api import deps
from app.core.database import get_db
from app.models.models import Category, User
from app.schemas.schemas import CategoryResponse, CategoryCreate

router = APIRouter()

@router.get("/", response_model=List[CategoryResponse])
async def read_categories(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    獲取所有分類。
    """
    result = await db.execute(select(Category))
    categories = result.scalars().all()
    return categories

@router.post("/", response_model=CategoryResponse)
async def create_category(
    *,
    db: AsyncSession = Depends(get_db),
    category_in: CategoryCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """
    建立新分類。
    """
    result = await db.execute(select(Category).where(Category.name == category_in.name))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_obj = Category(**category_in.model_dump())
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj
