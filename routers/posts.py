from schemas import PostCreate, PostResponse, PostUpdate, PaginatedPostResponse
from database import get_db
from typing import Annotated, List
from fastapi import HTTPException, status, Depends, APIRouter, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import models 
from auth import CurrentUser

router = APIRouter()

#to get ALL POSTS
@router.get("", response_model = PaginatedPostResponse)
async def get_posts(db: Annotated[AsyncSession, Depends(get_db)], skip:Annotated[int,Query(ge=0)]=0, limit:Annotated[int,Query(ge=1,le=100)]=10):
    count_result = await db.execute(select(func.count()).select_from(models.Post))
    total = count_result.scalar() or 0
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).order_by(models.Post.date_posted.desc()).offset(skip).limit(limit))
    posts =  result.scalars().all()

    has_more = skip + len(posts) < total

    return PaginatedPostResponse(
        posts = [PostResponse.model_validate(post) for post in posts],
        total = total,
        skip = skip,
        limit = limit,
        has_more = has_more
    )

#GET POST BASED ON POST ID
@router.get("/{post_id}", response_model = PostResponse)
async def get_post(post_id : int, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    existing_result = result.scalars().first()
    if existing_result:
        return existing_result
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,detail='Post Not Found')

#POST FULL UPDATE
@router.put("/{post_id}", response_model = PostResponse)
async def post_fullUpdate(post_id: int, post_data: PostCreate, current_user : CurrentUser, db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail='Post Not Found')
    if post.user_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Not authorized to update this post")  
    
    post.title = post_data.title
    post.content = post_data.content

    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post
    
#POST PARTIAL UPDATE
@router.patch("/{post_id}", response_model = PostResponse)
async def post_partialUpdate(post_id: int, post_data: PostUpdate, current_user : CurrentUser,  db:Annotated[AsyncSession,Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail='Post Not Found')

    if post.user_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Not authorized to update this post")  

    update_data = post_data.model_dump(exclude_unset=True)
    for key,value in update_data.items():
        setattr(post,key,value)
        
    await db.commit()
    await db.refresh(post, attribute_names = ["author"])
    return post

#CREATE POST
@router.post("", response_model = PostResponse,status_code = status.HTTP_201_CREATED )
async def create_post(post : PostCreate,current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):

    new_post =models.Post(title=post.title,content=post.content,user_id =current_user.id)

    db.add(new_post)
    await db.commit()
    await db.refresh(new_post, attribute_names = ["author"])
    return new_post

#DELETE POST
@router.delete("/del/{post_id}",status_code = status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int , current_user : CurrentUser, db: Annotated[AsyncSession, Depends(get_db)]):
    result = await db.execute(select(models.Post).options(selectinload(models.Post.author)).where(models.Post.id == post_id))
    post = result.scalars().first()
    if not post:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail='Post Not Found')

    if post.user_id != current_user.id:
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "Not authorized to delete this post")  

    await db.delete(post)
    await db.commit()