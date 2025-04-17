from pydantic import BaseModel, Field
from typing import List
class FragranceSchema(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    company: "CompanySchema"
    class Config:
        orm_mode = True

class FragranceUpdate(BaseModel):
    name: str | None = Field(min_length=3, max_length=150) 
    company_id: int | None = None
    
class CompanySchema(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=3, max_length=250)
    class Config:
        orm_mode = True

    
class ListFragranceResponseSchema(BaseModel):
    fragrance: List[FragranceSchema]
    class Config:
        orm_mode = True