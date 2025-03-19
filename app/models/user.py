"""
User models for the Travel Agent.

This module defines the data models for users and their preferences.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import re


class TravelPreference(BaseModel):
    """User travel preference for a specific destination."""
    
    destination: str
    flexible_dates: bool = True
    budget: Optional[float] = None
    preferred_airlines: List[str] = Field(default_factory=list)
    preferred_times: Optional[Dict[str, str]] = None  # e.g. {"departure": "morning", "return": "evening"}


class UserPreferences(BaseModel):
    """User preferences for travel."""
    
    home_airports: List[str]
    travel_preferences: List[TravelPreference] = Field(default_factory=list)
    preferred_airlines: List[str] = Field(default_factory=list)
    seat_class: str = "economy"  # economy, premium_economy, business, first


class User(BaseModel):
    """User model."""
    
    id: str
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    preferences: Optional[UserPreferences] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Simple validation for phone number format
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v
    
    def dict(self, *args, **kwargs):
        user_dict = super().dict(*args, **kwargs)
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        user_dict["updated_at"] = user_dict["updated_at"].isoformat()
        return user_dict


class SearchHistory(BaseModel):
    """User search history."""
    
    id: str
    user_id: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    search_timestamp: datetime = Field(default_factory=datetime.now)
    results: List[Dict[str, Any]] = Field(default_factory=list)
    lowest_price: Optional[float] = None
    
    def dict(self, *args, **kwargs):
        search_dict = super().dict(*args, **kwargs)
        search_dict["search_timestamp"] = search_dict["search_timestamp"].isoformat()
        return search_dict


class FlightDeal(BaseModel):
    """Flight deal model."""
    
    id: str
    user_id: str
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    price: float
    airline: str
    deal_quality: str  # great, good, normal
    price_difference_percentage: float  # negative means below average
    found_at: datetime = Field(default_factory=datetime.now)
    details: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self, *args, **kwargs):
        """Convert to dict with proper datetime handling."""
        result = super().dict(*args, **kwargs)
        if result.get("found_at"):
            result["found_at"] = result["found_at"].isoformat()
        return result


class UserCreate(BaseModel):
    phone_number: str
    name: Optional[str] = None
    email: Optional[str] = None
    
class UserResponse(BaseModel):
    id: str
    phone_number: str
    name: Optional[str] = None
    created_at: datetime
    has_preferences: bool 

    @validator('phone_number')
    def validate_phone_number(cls, v):
        # Simple validation for phone number format
        if not re.match(r'^\+?[0-9]{10,15}$', v):
            raise ValueError('Invalid phone number format')
        return v 

class Message:
    """Message in a conversation."""
    
    def __init__(self, role: str, content: str, timestamp: datetime = None):
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
    
    def dict(self):
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        timestamp = datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else None
        return cls(
            role=data.get("role", "user"),
            content=data.get("content", ""),
            timestamp=timestamp
        )

class Conversation:
    """Conversation history."""
    
    def __init__(self, id: str, user_id: str, messages: List[Message] = None, created_at: datetime = None, updated_at: datetime = None):
        self.id = id
        self.user_id = user_id
        self.messages = messages or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def add_message(self, role: str, content: str) -> Message:
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": [message.dict() for message in self.messages],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        messages = [Message.from_dict(msg) for msg in data.get("messages", [])]
        created_at = datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None
        updated_at = datetime.fromisoformat(data.get("updated_at")) if data.get("updated_at") else None
        
        return cls(
            id=data.get("id", ""),
            user_id=data.get("user_id", ""),
            messages=messages,
            created_at=created_at,
            updated_at=updated_at
        ) 