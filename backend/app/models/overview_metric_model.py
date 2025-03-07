from pydantic import BaseModel, Field
from typing import Literal, Optional

class OverViewMetric(BaseModel):
  label: str = Field(..., description="The label of the metric")
  delta: Optional[int | str] = Field(None, description="The change in the metric or additional information") 
  value: int | str | None = Field(..., description="The value of the metric")
  delta_type: Optional[Literal["increase", "decrease"]] = None
  help: Optional[str] = Field(None, description="Help text for the metric")