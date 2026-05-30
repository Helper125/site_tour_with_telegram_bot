from pydantic import BaseModel

class LandCreate(BaseModel):
    name: str

class LandUpdate(BaseModel):
    name: str | None = None

    model_config = {"from_attributes": True}

class CityCreate(BaseModel):
    name: str
    land_id: int

class CityUpdate(BaseModel):
    name: str | None = None
    land_id: int | None = None

    model_config = {"from_attributes": True}


class LandmarkCreate(BaseModel):
    name: str
    description: str
    address: str
    city_id: int

class LandmarkUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    address: str | None = None
    city_id: int | None = None

    model_config = {"from_attributes": True}