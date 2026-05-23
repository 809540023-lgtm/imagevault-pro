from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.database import engine, Base

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 設定 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 掛載 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

# 掛載靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return FileResponse("static/dashboard.html")

@app.get("/dashboard")
async def dashboard():
    return FileResponse("static/dashboard.html")

# 注意：在生產環境中建議使用 Alembic 進行遷移
# 這裡為了演示方便，提供一個初始化資料庫的端點（僅限開發環境）
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all) # 慎用
        await conn.run_sync(Base.metadata.create_all)
