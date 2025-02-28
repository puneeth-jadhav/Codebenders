# Flight Booking Backend API

## Project Overview
This is a backend API for a flight booking system built with FastAPI, SQLAlchemy, and SQLite.

## Tech Stack
- Framework: FastAPI (0.104.1)
- Database: SQLite with SQLAlchemy ORM
- Python Version: 3.11

## Setup Instructions

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Environment Variables
Create a `.env` file with the following:
```
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=your_secret_key_here
DEBUG=True
```

### 4. Run Database Migrations
The database will be automatically created when you start the server.

### 5. Start the Server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Users
- `POST /users`: Create a new user
- `GET /users/{user_id}`: Get user details

### Flights
- `GET /flights`: Search available flights
- `GET /flights/{flight_id}`: Get flight details

### Bookings
- `POST /bookings`: Create a new booking
- `GET /bookings/{booking_id}`: Get booking details

### Fares
- `GET /fares`: List all fare types
- `GET /fares/{fare_id}`: Get specific fare details

## Testing
Access Swagger UI documentation at `http://localhost:8000/docs`

## Notes
- Uses SQLite for lightweight database
- Includes basic error handling
- Follows RESTful API conventions