from pydantic import BaseModel


class UserPostIn(BaseModel):  # inherits BaseModel
    body: str


class UserPost(UserPostIn):
    id: int
