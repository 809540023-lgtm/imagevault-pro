from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.api import deps
from app.core.database import get_db, get_mongo_collection
from app.models.models import Image, User, Category
from app.schemas.schemas import ImageResponse
from app.services.image_service import ImageService
from app.services.s3_service import s3_service

router = APIRouter()

@router.post("/", response_model=ImageResponse)
async def upload_image(
    *,
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    category_name: str = Form("default"),
    warehouse_location: str = Form("未知"),
    tags: str = Form(""),
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    上傳圖片並儲存元數據。
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    
    image_obj, cat_name = await ImageService.handle_image_upload(
        db=db,
        file_data=contents,
        category_name=category_name,
        warehouse_location=warehouse_location,
        tags=tag_list,
        user_id=current_user.id
    )
    
    return ImageResponse(
        id=image_obj.id,
        filename=image_obj.filename,
        s3_url=image_obj.s3_url,
        warehouse_location=image_obj.warehouse_location,
        upload_date=image_obj.upload_date,
        category_name=cat_name,
        tags=tag_list
    )

@router.get("/", response_model=List[ImageResponse])
async def read_images(
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = None,
    current_user: User = Depends(deps.get_current_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    獲取當前使用者的圖片列表。
    """
    query = select(Image).options(joinedload(Image.category)).where(Image.owner_id == current_user.id)
    
    if category:
        query = query.join(Category).where(Category.name == category)
    
    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    images = result.scalars().all()
    
    # 獲取標籤
    tags_collection = get_mongo_collection("image_tags")
    
    response_images = []
    for img in images:
        tags = []
        try:
            tags_doc = await tags_collection.find_one({"image_id": img.id})
            tags = tags_doc["tags"] if tags_doc else []
        except Exception:
            pass
        
        response_images.append(
            ImageResponse(
                id=img.id,
                filename=img.filename,
                s3_url=img.s3_url,
                warehouse_location=img.warehouse_location,
                upload_date=img.upload_date,
                category_name=img.category.name,
                tags=tags
            )
        )
    
    return response_images

@router.get("/{id}", response_model=ImageResponse)
async def read_image(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    獲取單一圖片詳情。
    """
    result = await db.execute(
        select(Image).options(joinedload(Image.category))
        .where(Image.id == id, Image.owner_id == current_user.id)
    )
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 獲取標籤
    tags = []
    try:
        tags_collection = get_mongo_collection("image_tags")
        tags_doc = await tags_collection.find_one({"image_id": image.id})
        tags = tags_doc["tags"] if tags_doc else []
    except Exception:
        pass

    return ImageResponse(
        id=image.id,
        filename=image.filename,
        s3_url=image.s3_url,
        warehouse_location=image.warehouse_location,
        upload_date=image.upload_date,
        category_name=image.category.name,
        tags=tags
    )

@router.delete("/{id}")
async def delete_image(
    *,
    db: AsyncSession = Depends(get_db),
    id: int,
    current_user: User = Depends(deps.get_current_user)
) -> Any:
    """
    刪除圖片。
    """
    result = await db.execute(select(Image).where(Image.id == id, Image.owner_id == current_user.id))
    image = result.scalar_one_or_none()
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # 1. 刪除 S3 檔案
    await s3_service.delete_image(image.filename)
    
    # 2. 刪除 MongoDB 標籤
    tags_collection = get_mongo_collection("image_tags")
    await tags_collection.delete_one({"image_id": id})
    
    # 3. 刪除 PostgreSQL 記錄
    await db.delete(image)
    await db.commit()
    
    return {"msg": "Image deleted"}
