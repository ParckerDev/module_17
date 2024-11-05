from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    username: str
    password_hash: str

class Task(BaseModel):
    id: int
    title: str
    description: str
    status: str  # Например, "в процессе" или "завершена"
    user_id: int
