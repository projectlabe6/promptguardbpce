from typing import Any, Dict

from pydantic import BaseModel, Field


class IngestedContent(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
