from pydantic import BaseModel, Field


class Entity(BaseModel):
    type: str
    value: str
    start: int = Field(..., ge=0)
    end: int = Field(..., ge=0)
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    source: str = Field("rules")
