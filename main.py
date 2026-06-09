from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from sqlalchemy.ext.asyncio import AsyncSession
import models 
from database import Base, engine, get_db
from contextlib import asynccontextmanager
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler

from routers import posts,users


#Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(_app: FastAPI):
    #Startup
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield 
    #Shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

app.mount("/static",StaticFiles(directory ="static"),name = "static")


templates = Jinja2Templates(directory = "templates")

app.include_router(users.router,prefix="/api/users",tags=["users"])
app.include_router(posts.router,prefix="/api/posts",tags=["posts"])

# @app.get("/", include_in_schema = False)
# @app.get("/posts",include_in_schema = False)
# def home(request:Request):
#     return templates.TemplateResponse(request,"home.html",{'posts':posts, "title": "Home"})










    