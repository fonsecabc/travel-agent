from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class FlightSegment(BaseModel):
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: datetime
    arrival_time: datetime
    duration_minutes: int
    cabin_class: str

class FlightItinerary(BaseModel):
    segments: List[FlightSegment]
    total_duration_minutes: int
    stops: int
    price: float
    currency: str = "USD"
    booking_link: Optional[str] = None
    booking_site: Optional[str] = None
    
class Deal(BaseModel):
    id: Optional[str] = None
    user_id: str
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    price: float
    currency: str = "USD"
    airline: str
    cabin_class: str
    booking_link: str
    price_drop_percentage: Optional[float] = None
    expiration_time: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)
    itinerary: FlightItinerary
    
class Trip(BaseModel):
    id: Optional[str] = None
    user_id: str
    status: str = Field("wishlist", description="Trip status: wishlist, planned, booked, completed, cancelled")
    origin: str
    destination: str
    departure_date: datetime
    return_date: Optional[datetime] = None
    budget: Optional[float] = None
    flexible_dates: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    booked_itinerary: Optional[FlightItinerary] = None
    
class SearchHistory(BaseModel):
    id: Optional[str] = None
    user_id: str
    search_params: Dict[str, Any]
    search_time: datetime = Field(default_factory=datetime.now)
    results_count: int
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    avg_price: Optional[float] = None
    
class Notification(BaseModel):
    id: Optional[str] = None
    user_id: str
    deal_id: Optional[str] = None
    message: str
    sent_at: datetime = Field(default_factory=datetime.now)
    read: bool = False
    clicked: bool = False 