from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional, List

# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int
    created_at: Optional[date] = None

    class Config:
        orm_mode = True

# Flight Schemas
class FlightBase(BaseModel):
    flight_number: str
    airline: str
    departure_city: str
    arrival_city: str
    departure_date: date
    return_date: Optional[date] = None
    travel_class: str
    available_seats: int

class FlightCreate(FlightBase):
    pass

class Flight(FlightBase):
    flight_id: int

    class Config:
        orm_mode = True

# Booking Schemas
class BookingBase(BaseModel):
    user_id: int
    flight_id: int
    fare_id: int
    adults: int = Field(ge=0)
    children: int = Field(ge=0)
    infants: int = Field(ge=0)
    booking_date: date

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    booking_id: int

    class Config:
        orm_mode = True

# Fare Schemas
class FareBase(BaseModel):
    fare_type: str
    description: str

class FareCreate(FareBase):
    pass

class Fare(FareBase):
    fare_id: int

    class Config:
        orm_mode = True

# Error Response Schema
class ErrorResponse(BaseModel):
    code: int
    message: str