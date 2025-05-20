from pydantic import BaseModel, Field, field_validator
from typing import List
from backend.core.db.models.fragrance import FragranceType
class FragranceSchema(BaseModel):
    id: int
    name: str = Field(min_length=3, max_length=150)
    company: "CompanySchema"
    description: str | None = None
    fragrance_type: FragranceType
    price: int 
    ml: int | None = None
    picture: str | None = None
    accords: List["AccordResponseSchema"] | None = None
    class Config:
        from_attributes = True

class FragranceShemaById(FragranceSchema):
    reviews: List["ReviewResponseSchema"] | None = None


class FragranceRequestSchema(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    company_id: int
    description: str | None = None
    fragrance_type: FragranceType
    price: int 


class FragranceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=150) 
    company_id: int | None = None
    fragrance_type: FragranceType | None = None
    description: str | None = None
    price: int | None = None
    ml: int | None = None
    picture: str | None = None
    accords: list[int] | None = None
    
class CompanySchema(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=3, max_length=250)
    class Config:
        orm_mode = True

    
class ListFragranceResponseSchema(BaseModel):
    fragrance: List[FragranceSchema]
    class Config:
        orm_mode = True


class AccordRequestSchema(BaseModel):
    name: str
    description: str
    group_id: int
class AccordResponseSchema(BaseModel):
    name: str
    description: str
    group_id: int
class AccordUpdateSchema(BaseModel):
    name: str | None = None
    description: str | None = None
    group_id: int | None = None

class AccordGroupRequestSchema(BaseModel):
    name: str
    description: str


class ReviewResponseSchema(BaseModel):
    user_id: int
    content: int
    rating: float

class ReviewCreateSchema(BaseModel):
    content: str
    fragrance_id: int
    rating: float

class ReviewUpdateSchema(BaseModel):
    content: str | None = None
    rating: float | None = None

    @field_validator("rating")
    def valid_rating(cls, value: float) -> float:
        if not (1 <= value <= 10):
            raise ValueError("Rating must be between 1 and 10")
        if (value * 2) % 1 != 0:  
            raise ValueError("Rating must be a multiple of 0.5 (e.g., 1.0, 1.5, 2.0)")
        return value