from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchemas(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    is_admin: Optional[bool]