from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    
    bookings = relationship("Booking", back_populates="user")

class Flight(Base):
    __tablename__ = "flights"

    flight_id = Column(Integer, primary_key=True, index=True)
    flight_number = Column(String, index=True)
    airline = Column(String)
    departure_city = Column(String)
    arrival_city = Column(String)
    departure_date = Column(Date)
    return_date = Column(Date, nullable=True)
    travel_class = Column(String)
    available_seats = Column(Integer)
    
    bookings = relationship("Booking", back_populates="flight")

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    flight_id = Column(Integer, ForeignKey("flights.flight_id"))
    fare_id = Column(Integer, ForeignKey("fares.fare_id"))
    adults = Column(Integer)
    children = Column(Integer)
    infants = Column(Integer)
    booking_date = Column(Date)
    
    user = relationship("User", back_populates="bookings")
    flight = relationship("Flight", back_populates="bookings")
    fare = relationship("Fare", back_populates="bookings")

class Fare(Base):
    __tablename__ = "fares"

    fare_id = Column(Integer, primary_key=True, index=True)
    fare_type = Column(String)
    description = Column(String)
    
    bookings = relationship("Booking", back_populates="fare")