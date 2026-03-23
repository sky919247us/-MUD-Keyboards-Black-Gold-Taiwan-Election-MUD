import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# 讀取連線字串，如果尚未設定預設連回本地端 SQLite
DATABASE_URL = settings.DATABASE_URL

# 建立 SQLAlchemy AsyncEngine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG, # 印出 SQL 語句
    future=True,
)

# 建立 Session Factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    expire_on_commit=False
)

# SQLAlchemy 宣告基底
Base = declarative_base()

async def get_db():
    """FastAPI Depends 供注入用的資料庫連線"""
    async with AsyncSessionLocal() as session:
        yield session
