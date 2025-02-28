from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from typing import List, Optional
import schemas
from datetime import date, datetime

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Flight Booking API",
    description="API for managing flight bookings",
    version="1.0.0"
)

# Users Endpoints
@app.post("/users", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if email already exists
        existing_user = db.query(models.User).filter(models.User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        db_user = models.User(
            name=user.name, 
            email=user.email, 
            phone=user.phone
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Flights Endpoints
@app.get("/flights", response_model=List[schemas.Flight])
def search_flights(
    departure_city: str, 
    arrival_city: str, 
    departure_date: date, 
    return_date: Optional[date] = None, 
    travel_class: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(models.Flight).filter(
        models.Flight.departure_city == departure_city,
        models.Flight.arrival_city == arrival_city,
        models.Flight.departure_date == departure_date
    )
    
    if travel_class:
        query = query.filter(models.Flight.travel_class == travel_class)
    
    flights = query.all()
    
    if not flights:
        raise HTTPException(status_code=404, detail="No flights found")
    
    return flights

@app.get("/flights/{flight_id}", response_model=schemas.Flight)
def get_flight(flight_id: int, db: Session = Depends(get_db)):
    flight = db.query(models.Flight).filter(models.Flight.flight_id == flight_id).first()
    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")
    return flight

# Bookings Endpoints
@app.post("/bookings", response_model=schemas.Booking)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    try:
        # Validate user exists
        user = db.query(models.User).filter(models.User.user_id == booking.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Validate flight exists and has available seats
        flight = db.query(models.Flight).filter(models.Flight.flight_id == booking.flight_id).first()
        if not flight:
            raise HTTPException(status_code=404, detail="Flight not found")
        
        total_passengers = booking.adults + booking.children + booking.infants
        if total_passengers > flight.available_seats:
            raise HTTPException(status_code=400, detail="Not enough available seats")
        
        # Validate fare exists
        fare = db.query(models.Fare).filter(models.Fare.fare_id == booking.fare_id).first()
        if not fare:
            raise HTTPException(status_code=404, detail="Fare not found")
        
        # Create booking
        db_booking = models.Booking(
            user_id=booking.user_id,
            flight_id=booking.flight_id,
            fare_id=booking.fare_id,
            adults=booking.adults,
            children=booking.children,
            infants=booking.infants,
            booking_date=booking.booking_date
        )
        
        # Update available seats
        flight.available_seats -= total_passengers
        
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        
        return db_booking
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookings/{booking_id}", response_model=schemas.Booking)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

# Fares Endpoints
@app.get("/fares", response_model=List[schemas.Fare])
def list_fares(db: Session = Depends(get_db)):
    fares = db.query(models.Fare).all()
    if not fares:
        raise HTTPException(status_code=404, detail="No fares found")
    return fares

@app.get("/fares/{fare_id}", response_model=schemas.Fare)
def get_fare(fare_id: int, db: Session = Depends(get_db)):
    fare = db.query(models.Fare).filter(models.Fare.fare_id == fare_id).first()
    if not fare:
        raise HTTPException(status_code=404, detail="Fare not found")
    return fare

# Optional: Add some initial data for testing
def init_test_data(db: Session):
    # Create some initial fares
    fares = [
        models.Fare(fare_type="Standard", description="Regular fare"),
        models.Fare(fare_type="Special", description="Discounted fare")
    ]
    db.add_all(fares)
    
    # Create some initial flights
    flights = [
        models.Flight(
            flight_number="FL001", 
            airline="Sky Airlines", 
            departure_city="New York", 
            arrival_city="Los Angeles", 
            departure_date=date.today(), 
            travel_class="Economy", 
            available_seats=50
        ),
        models.Flight(
            flight_number="FL002", 
            airline="Global Airways", 
            departure_city="Chicago", 
            arrival_city="Miami", 
            departure_date=date.today(), 
            travel_class="Business", 
            available_seats=20
        )
    ]
    db.add_all(flights)
    
    db.commit()

# Startup event to initialize test data
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    init_test_data(db)

# Optional: Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}