from fastapi import APIRouter, HTTPException

from storeapi.database import comment_table, post_table, database
from storeapi.models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

router = APIRouter()


async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)

    return await database.fetch_one(query)


@router.post("/post", response_model=UserPost)
async def create_post(post: UserPostIn):
    data = post.dict()
    query = post_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
    # last_record_id = len(post_table)
    # new_post = {**data, "id": last_record_id}
    # post_table[last_record_id] = new_post
    # return new_post


@router.get("/post", response_model=list[UserPost])
async def get_all_posts():
    query = post_table.select()
    return await database.fetch_all(query)  # return_valud["body"]


@router.post("/comment", response_model=Comment)
async def create_post(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    data = comment.dict()
    query = comment_table.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}
    # last_record_id = len(comment_table)
    # new_comment = {**data, "id": last_record_id}
    # comment_table[last_record_id] = new_comment
    # return new_comment


@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comments_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)
    # return [
    #     comment for comment in comment_table.values() if comment["post_id"] == post_id
    # ]


@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_with_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "post": post,
        "comments": await get_comments_on_post(post_id)
    }
