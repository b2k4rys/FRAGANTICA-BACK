from pydantic import BaseModel, Field

class FragranceSchema(BaseModel):
    name: str = Field(min_length=3, max_length=150)
    