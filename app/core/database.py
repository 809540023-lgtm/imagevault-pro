from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# 資料庫非同步引擎
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite 專用配置，解決 "database is locked" 問題
    engine = create_async_engine(
        settings.DATABASE_URL, 
        echo=False,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

# 非同步 Session 工廠
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# SQLAlchemy 基礎類
class Base(DeclarativeBase):
    pass

# MongoDB 客戶端
mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
mongo_db = mongo_client[settings.MONGO_DB_NAME]

# 獲取資料庫 Session 的依賴項
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

# 獲取 MongoDB 集合的工具函數
def get_mongo_collection(collection_name: str):
    return mongo_db[collection_name]
