#from sqlalchemy import create_engine
#from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from config import settings

#SQLALCHEMY_DATABSE_URL = "sqlite:///./blog.db"
#SQLALCHEMY_DATABSE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(settings.database_url,connect_args={"ssl": True})

#SessionLocal = sessionmaker(autocommit=False, autoflush = False, bind = engine)
AsyncSessionLocal = async_sessionmaker(engine, class_ = AsyncSession, expire_on_commit = False)

async def get_db():
        async with AsyncSessionLocal() as session:
            yield session

class Base(DeclarativeBase):
    pass