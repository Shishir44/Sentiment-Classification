from pydantic import BaseModel, field_validator, Field
from datetime import datetime

class DateFilters(BaseModel):
    start_date: str = Field("2024-11-05", description="The start date of the date range")
    end_date: str = Field("2024-11-07", description="The end date of the date range")

    @field_validator("start_date", "end_date")
    def validate_dates(cls, value, field):
        try:
            date_ = datetime.strptime(value, "%Y-%m-%d")
            return date_
        except ValueError:
            raise ValueError(f"Invalid date format for {field}")