from pydantic import BaseModel, field_validator, constr
from typing import Any, Optional
from datetime import datetime

class Request(BaseModel):
    user_id: Optional[int | Any]
    user_name: Optional[str]
    comment_id: Optional[int | Any]
    comment_text: Optional[str]
    comment_date: Optional[str | Any]
    post_id: Optional[int | Any]
    post_title: Optional[str]
    post_caption: Optional[str]
    post_date: Optional[str | Any]
    
    @field_validator("comment_date","post_date")
    def validate_comment_date(cls, v):
        try:
            if not v:
                return None
            return datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except:
            return None