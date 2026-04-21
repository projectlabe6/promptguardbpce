from typing import Dict

from pydantic import BaseModel, Field


class WeightsUpdate(BaseModel):
    weights: Dict[str, float] = Field(...)
