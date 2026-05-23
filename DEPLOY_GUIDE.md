# ImageVault Pro 永久網站部署指南

本指南將協助您將 ImageVault Pro 從開發環境遷移到永久運行的雲端平台。

## 1. 準備工作
- **GitHub 帳號**: 用於託管程式碼。
- **雲端平台帳號**: 推薦使用 [Railway](https://railway.app/) 或 [Render](https://render.com/)。
- **S3 存儲 (選配)**: 推薦使用 AWS S3 或 Cloudflare R2 以實現永久圖片存儲。

## 2. 部署方式 (推薦：Railway)
Railway 是目前最簡單的永久化方案：
1. 將本專案程式碼上傳至您的 GitHub 倉庫。
2. 在 Railway 點擊 `New Project` -> `Deploy from GitHub repo`。
3. Railway 會自動識別 `Dockerfile` 並開始構建。
4. **配置環境變數**: 在 Railway 的 `Variables` 頁面填入 `.env` 中的內容。

## 3. 資料庫永久化
- **本地模式**: 系統預設使用 SQLite，數據會儲存在容器卷中。
- **雲端模式**: 建議在 Railway 建立一個 PostgreSQL 實例，並將 `DATABASE_URL` 更新為雲端網址。

## 4. 檔案清單
- `Dockerfile`: 生產環境鏡像配置。
- `docker-compose.yml`: 本地生產環境模擬。
- `requirements.txt`: 所有必要的 Python 依賴。
- `.env.example`: 環境變數範本。

## 5. 聯絡與支援
如果您在部署過程中遇到任何問題，請隨時聯繫您的 AI 助手。
