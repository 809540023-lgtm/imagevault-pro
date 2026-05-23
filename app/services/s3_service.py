import aioboto3
from app.core.config import settings
import uuid
import os

class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()
        self.bucket = settings.S3_BUCKET
        self.region = settings.AWS_REGION

    async def upload_image(self, file_data: bytes, content_type: str = "image/jpeg") -> str:
        """
        上傳圖片到 S3 並返回公開 URL。若無憑證則儲存至本地 static 目錄。
        """
        filename = f"{uuid.uuid4()}.jpg"
        
        # 檢查是否使用模擬模式
        is_mock = not settings.AWS_ACCESS_KEY_ID or settings.AWS_ACCESS_KEY_ID in ["your_key", "mock-key", ""]
        
        if is_mock:
            # 本地模擬儲存 (永久網站建議配置 S3，但保留此選項作為備援)
            os.makedirs("static/uploads", exist_ok=True)
            file_path = os.path.join("static/uploads", filename)
            with open(file_path, "wb") as f:
                f.write(file_data)
            return f"/static/uploads/{filename}"
        
        async with self.session.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as s3:
            await s3.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=file_data,
                ContentType=content_type
            )
            
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{filename}"

    async def delete_image(self, filename: str):
        """
        從 S3 刪除圖片。
        """
        if os.path.exists(os.path.join("static/uploads", filename)):
            os.remove(os.path.join("static/uploads", filename))
            return

        async with self.session.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
        ) as s3:
            await s3.delete_object(Bucket=self.bucket, Key=filename)

s3_service = S3Service()
