from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class VisualizeRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    drug_name: Optional[str] = None
    compare_drug_name: Optional[str] = None
    condition: Optional[str] = None
    trial_phase: Optional[str] = None
    sponsor: Optional[str] = None
    country: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    overall_status: Optional[str] = None
    max_studies: int = Field(default=100, ge=1, le=300)
    use_llm: bool = True


class VisualizationResponse(BaseModel):
    visualization: Dict[str, Any]
    meta: Dict[str, Any]