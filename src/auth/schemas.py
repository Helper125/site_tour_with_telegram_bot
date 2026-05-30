from pydantic import BaseModel, Field, EmailStr

class Register(BaseModel):
    username: str = Field(min_length=5, max_length=100)
    email: EmailStr
    password: str = Field(min_length=5, max_length=350)


class Login(BaseModel):
    email: EmailStr
    password: str