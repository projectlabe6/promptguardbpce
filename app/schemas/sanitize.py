from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.schemas.entity import Entity


class SanitizeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class SanitizeResponse(BaseModel):
    decision: str
    risk_score: float = Field(..., ge=0.0, le=100.0)
    sanitized_text: str
    entities: List[Entity] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    execution_time_ms: Optional[float] = None
