import io
import os
from PIL import Image
import pillow_heif
from app.core.config import settings

# 註冊 HEIF 開啟器以支援 HEIC 格式
pillow_heif.register_heif_opener()

class ImageProcessor:
    @staticmethod
    async def process_image(image_data: bytes) -> bytes:
        """
        優化後的圖片處理：支援高像素檔案，並在記憶體中高效轉換與壓縮。
        """
        try:
            # 讀取圖片數據
            img = Image.open(io.BytesIO(image_data))
            
            # 1. 統一轉換為 RGB (JPEG 支援)
            if img.mode != "RGB":
                img = img.convert("RGB")
            
            # 2. 檢查像素是否過高 (例如 4K 以上)，後端進行二次縮放以確保系統穩定
            MAX_PIXELS = 3840 
            if max(img.size) > MAX_PIXELS:
                img.thumbnail((MAX_PIXELS, MAX_PIXELS), Image.Resampling.LANCZOS)
            
            # 3. 設定最大檔案大小限制
            max_size = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
            quality = settings.IMAGE_QUALITY
            
            output = io.BytesIO()
            img.save(output, format="JPEG", quality=quality, optimize=True)
            processed_data = output.getvalue()
            
            # 4. 如果壓縮後仍然太大，則逐步降低品質與尺寸
            while len(processed_data) > max_size and quality > 50:
                quality -= 10
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=quality, optimize=True)
                processed_data = output.getvalue()
                
            # 5. 如果品質降低後還是太大，則進行尺寸縮放
            while len(processed_data) > max_size:
                new_width = int(img.width * 0.8)
                new_height = int(img.height * 0.8)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                output = io.BytesIO()
                img.save(output, format="JPEG", quality=quality, optimize=True)
                processed_data = output.getvalue()
                
            return processed_data
        except Exception as e:
            raise Exception(f"圖片引擎處理失敗: {str(e)}")
