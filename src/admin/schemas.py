from pydantic import BaseModel, EmailStr
from typing import Optional


class UserSchemas(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    is_admin: Optional[bool]

class UserCreate(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    is_admin: Optional[bool]
    password: Optional[str]


class LandCreate(BaseModel):
    name: Optional[str]


class CityCreate(BaseModel):
    name: Optional[str]
    land_id: Optional[int]


class LandmarkCreate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    description: Optional[str]
    city_id: Optional[int]