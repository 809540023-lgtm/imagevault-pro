# 使用官方 Python 3.11 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴 (包含圖片處理所需的庫)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libheif-dev \
    libde265-dev \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴清單並安裝
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt aiosqlite

# 複製專案程式碼
COPY . .

# 建立上傳目錄
RUN mkdir -p static/uploads

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 開放埠口
EXPOSE 8000

# 啟動服務
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
