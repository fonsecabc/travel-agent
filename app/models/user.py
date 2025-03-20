import re
import uuid

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

class User(BaseModel):
    """User model."""
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    phone_number: str
    name: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)

    @validator('phone_number')
    def validate_phone_number(cls, v):
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

