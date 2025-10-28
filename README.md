# Taxi Track API

A Flask-based REST API for taxi tracking and management system. This application provides endpoints for mobile taxi apps to track taxi availability, trip details, and rank information.

## Features

- **Taxi Management**: Track taxi locations, status, and availability
- **Trip Tracking**: Monitor active trips, passenger counts, and estimated completion times
- **Rank Analytics**: View taxi availability at different ranks
- **User Management**: Handle user accounts and trip history
- **Real-time Updates**: Get current taxi status and trip information

## API Endpoints

### Ranks
- `GET /api/ranks` - Get all taxi ranks
- `GET /api/ranks/<id>` - Get specific rank details
- `GET /api/ranks/<id>/taxis` - Get taxis at a specific rank

### Taxis
- `GET /api/taxis` - Get all taxis (with optional filtering)
- `GET /api/taxis/<id>` - Get specific taxi details
- `GET /api/taxis/<id>/trips` - Get trip history for a taxi

### Trips
- `GET /api/trips` - Get all trips (with optional filtering)
- `POST /api/trips` - Create a new trip
- `GET /api/trips/<id>` - Get specific trip details
- `PUT /api/trips/<id>/complete` - Mark trip as completed
- `PUT /api/trips/<id>/cancel` - Cancel a trip

### Analytics
- `GET /api/analytics/rank/<id>` - Get rank analytics
- `GET /api/analytics/daily` - Get daily analytics

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/<id>` - Get user details
- `GET /api/users/<id>/trips` - Get user trip history

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd taxi_track
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MySQL database**
   - Create a MySQL database named `taxi_track`
   - Update database credentials in `config.py` or set environment variables

4. **Initialize the database**
   ```bash
   python database_setup.py
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
DATABASE_URL=mysql+pymysql://username:password@localhost/taxi_track
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=username
MYSQL_PASSWORD=password
MYSQL_DATABASE=taxi_track
```

## Database Schema

### Ranks
- `id`: Primary key
- `name`: Rank name
- `location`: Physical address
- `latitude/longitude`: GPS coordinates
- `max_capacity`: Maximum number of taxis

### Taxis
- `id`: Primary key
- `registration_number`: Taxi registration
- `driver_name`: Driver's name
- `driver_phone`: Driver's contact
- `capacity`: Passenger capacity
- `status`: available/on_trip/offline
- `rank_id`: Foreign key to ranks

### Trips
- `id`: Primary key
- `taxi_id`: Foreign key to taxis
- `user_id`: Foreign key to users (optional)
- `pickup/dropoff_location`: Trip locations
- `pickup/dropoff_latitude/longitude`: GPS coordinates
- `passenger_count`: Number of passengers
- `status`: active/completed/cancelled
- `estimated_duration`: Expected trip time (minutes)
- `actual_duration`: Actual trip time (minutes)
- `fare`: Trip cost
- `started_at/completed_at`: Timestamps

### Users
- `id`: Primary key
- `username`: Unique username
- `email`: Email address
- `phone`: Phone number

## Usage Examples

### Get available taxis at a rank
```bash
curl http://localhost:5000/api/ranks/1/taxis
```

### Create a new trip
```bash
curl -X POST http://localhost:5000/api/trips \
  -H "Content-Type: application/json" \
  -d '{
    "taxi_id": 1,
    "pickup_location": "Central Station",
    "dropoff_location": "Airport",
    "pickup_latitude": -26.2041,
    "pickup_longitude": 28.0473,
    "dropoff_latitude": -26.1332,
    "dropoff_longitude": 28.2411,
    "passenger_count": 2,
    "estimated_duration": 45
  }'
```

### Get rank analytics
```bash
curl http://localhost:5000/api/analytics/rank/1
```

## Development

The application uses Flask with SQLAlchemy for database operations. The code is organized into:

- `app.py`: Main Flask application
- `models.py`: SQLAlchemy models
- `routes.py`: API route handlers
- `config.py`: Configuration management
- `database_setup.py`: Database initialization script

## License

This project is licensed under the MIT License.

