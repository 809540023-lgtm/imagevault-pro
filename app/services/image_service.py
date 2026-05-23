from typing import List, Tuple
from datetime import datetime
from app.services.image_processor import ImageProcessor
from app.services.s3_service import S3Service
from app.core.database import get_mongo_collection
from app.models.models import Image, Category, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class ImageService:
    @staticmethod
    async def handle_image_upload(
        db: AsyncSession,
        file_data: bytes,
        user_id: int,
        category_name: str,
        warehouse_location: str,
        tags: List[str] = None
    ) -> Tuple[Image, str]:
        # 1. 處理圖片 (壓縮、HEIC 轉換)
        try:
            processed_data = await ImageProcessor.process_image(file_data)
        except Exception as e:
            raise Exception(f"圖片處理失敗: {str(e)}")
        
        # 2. 上傳到 S3
        try:
            s3_service = S3Service()
            s3_url = await s3_service.upload_image(processed_data)
        except Exception as e:
            raise Exception(f"存儲服務上傳失敗: {str(e)}")
            
        filename = s3_url.split("/")[-1]
        
        # 3. 處理分類 (查找或創建)
        result = await db.execute(select(Category).where(Category.name == category_name))
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(name=category_name)
            db.add(category)
            await db.flush()
            
        # 4. 儲存元數據到 PostgreSQL
        new_image = Image(
            filename=filename,
            s3_url=s3_url,
            owner_id=user_id, # 修正為模型中定義的 owner_id
            category_id=category.id,
            warehouse_location=warehouse_location
        )
        db.add(new_image)
        await db.flush()
        
        # 5. 儲存標籤到 MongoDB (增加錯誤處理以支援無 MongoDB 環境)
        if tags:
            try:
                tags_collection = get_mongo_collection("image_tags")
                await tags_collection.insert_one({
                    "image_id": new_image.id,
                    "tags": tags,
                    "created_at": datetime.utcnow()
                })
            except Exception as e:
                print(f"MongoDB 儲存失敗 (跳過): {e}")
            
        await db.commit()
        await db.refresh(new_image)
        
        return new_image, category.name
