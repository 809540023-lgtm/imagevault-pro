# ImageVault Pro 部署到 Railway 詳細教學指南

本指南將引導您完成將 **ImageVault Pro** 專案部署到 [Railway.app](https://railway.app/) 的所有步驟，讓您的應用程式擁有一個永久的線上網址，並具備生產級的穩定性與擴展性。

## 1. 前置準備

在開始部署之前，請確保您已完成以下準備工作：

*   **GitHub 帳號**：您需要一個 GitHub 帳號來託管您的專案程式碼。
*   **Railway 帳號**：您需要一個 Railway 帳號來部署您的應用程式。Railway 提供免費額度，適合初期使用。
*   **ImageVault Pro 專案程式碼**：您已從 Manus 下載並解壓縮 `imagevault_pro_release.zip` 到您的本地電腦。
*   **AWS S3 憑證 (可選)**：如果您希望使用 AWS S3 進行圖片存儲，請準備好您的 `AWS_ACCESS_KEY_ID`、`AWS_SECRET_ACCESS_KEY` 和 `S3_BUCKET` 名稱。若無，系統將預設使用本地存儲（不推薦用於生產環境）。

## 2. 將程式碼推送到 GitHub

1.  **建立新的 GitHub 倉庫**：
    *   登入您的 GitHub 帳號。
    *   點擊右上角的 `+` 號，選擇 `New repository`。
    *   輸入倉庫名稱，例如 `imagevault-pro`。
    *   選擇 `Private` 或 `Public` (建議 `Private` 以保護程式碼)。
    *   **不要勾選** `Add a README file`、`Add .gitignore` 或 `Choose a license`，我們將直接推送現有程式碼。
    *   點擊 `Create repository`。

2.  **推送本地程式碼到 GitHub**：
    *   打開您電腦上的終端機 (Terminal 或 CMD)。
    *   導航到您解壓縮 `imagevault_pro_release.zip` 的資料夾。
    *   執行以下 Git 指令：

    ```bash
    # 初始化 Git 倉庫
    git init

    # 將所有檔案加入暫存區
    git add .

    # 提交變更
    git commit -m "Initial release of ImageVault Pro"

    # 連結到您的 GitHub 遠端倉庫 (請將 <您的使用者名稱> 替換為您的 GitHub 使用者名稱)
    git remote add origin https://github.com/<您的使用者名稱>/imagevault-pro.git

    # 將程式碼推送到 GitHub
    git push -u origin main
    ```
    *   如果這是您第一次使用 Git 推送，系統可能會要求您輸入 GitHub 帳號和密碼，或使用個人存取令牌 (Personal Access Token)。

## 3. 在 Railway 上部署 ImageVault Pro

1.  **登入 Railway 並建立新專案**：
    *   前往 [Railway.app](https://railway.app/) 並登入。
    *   點擊左側導航欄的 `New Project` 或首頁的 `+ New Project`。
    *   選擇 `Deploy from GitHub Repo`。

2.  **連結 GitHub 帳號並選擇倉庫**：
    *   如果這是您第一次使用 Railway，它會要求您授權連結 GitHub 帳號。請按照指示完成授權。
    *   在倉庫列表中找到您剛才推送的 `imagevault-pro` 倉庫，點擊 `Deploy Now`。

3.  **配置環境變數**：
    *   Railway 會自動開始偵測您的專案並嘗試部署。在此之前，您需要設定環境變數。
    *   在部署頁面，點擊 `Variables` 選項卡。
    *   新增以下變數：

        | 變數名稱 | 範例值 (請替換為您的實際值) | 說明 |
        | :------- | :-------------------------- | :--- |
        | `DATABASE_URL` | `postgresql://user:password@host:port/dbname` | **重要**：這是您的 PostgreSQL 資料庫連接字串。我們將在下一步建立。 |
        | `MONGO_URL` | `mongodb://user:password@host:port/dbname` | **可選**：MongoDB 連接字串。如果不需要 MongoDB，可以留空或使用 `mongodb://localhost:27017/`。 |
        | `AWS_ACCESS_KEY_ID` | `您的AWS存取金鑰ID` | **可選**：AWS S3 存取金鑰。 |
        | `AWS_SECRET_ACCESS_KEY` | `您的AWS秘密存取金鑰` | **可選**：AWS S3 秘密存取金鑰。 |
        | `S3_BUCKET` | `您的S3儲存桶名稱` | **可選**：AWS S3 儲存桶名稱。 |
        | `SECRET_KEY` | `一個非常長的隨機字串` | **重要**：JWT 認證的秘密金鑰，請使用工具生成一個複雜的字串。 |
        | `ALGORITHM` | `HS256` | JWT 簽名演算法，預設為 HS256。 |
        | `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT 有效時間（分鐘）。 |

4.  **建立 PostgreSQL 資料庫**：
    *   回到 Railway 專案頁面，點擊 `+ New` -> `Database` -> `PostgreSQL`。
    *   Railway 會自動為您建立一個 PostgreSQL 服務，並生成 `DATABASE_URL`。複製這個 `DATABASE_URL`。
    *   回到您的 `imagevault-pro` 服務的 `Variables` 選項卡，將複製的 `DATABASE_URL` 貼到對應的變數中。

5.  **啟動部署**：
    *   完成環境變數設定後，Railway 會自動觸發部署。
    *   您可以在 `Deployments` 選項卡中查看部署進度與日誌。如果部署失敗，請檢查日誌中的錯誤訊息。

6.  **獲取應用程式網址**：
    *   部署成功後，點擊 `Settings` 選項卡。
    *   在 `Domains` 部分，您會看到一個由 Railway 提供的永久網址（例如 `imagevault-pro-xxxx.up.railway.app`）。
    *   您也可以在此設定自定義網域。

## 4. 部署後設定與測試

1.  **初始化資料庫**：
    *   由於 Railway 部署時會自動執行 `main.py`，其中的 `Base.metadata.create_all(bind=engine)` 會自動建立資料庫表格。
    *   如果遇到表格已存在的錯誤，可能需要手動連接到 Railway 的 PostgreSQL 資料庫，並刪除舊表格或使用 Alembic 進行遷移（本指南未涵蓋 Alembic）。

2.  **註冊第一個使用者**：
    *   訪問您的應用程式網址，然後導航到 `/docs` (例如 `https://imagevault-pro-xxxx.up.railway.app/docs`)。
    *   使用 Swagger UI 測試 `POST /api/v1/signup` 端點，註冊您的第一個管理員帳號。

3.  **測試功能**：
    *   登入 Dashboard (`/dashboard`)，測試拍照上傳、圖片瀏覽等功能。

## 5. 參考資料

*   [Railway 官方文件](https://docs.railway.app/)
*   [FastAPI 官方文件](https://fastapi.tiangolo.com/)
*   [Docker 官方文件](https://docs.docker.com/)

--- 

**作者：Manus AI**

**日期：2026年2月25日**

---
