"""
Utility functions for the Taxi Track application
"""

from flask import jsonify
from functools import wraps
import re

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone number format"""
    pattern = r'^\+?[1-9]\d{1,14}$'
    return re.match(pattern, phone) is not None

def validate_coordinates(latitude, longitude):
    """Validate GPS coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def handle_errors(f):
    """Decorator for error handling"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            return jsonify({'error': f'Invalid value: {str(e)}'}), 400
        except KeyError as e:
            return jsonify({'error': f'Missing required field: {str(e)}'}), 400
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    return decorated_function

def validate_trip_data(data):
    """Validate trip creation data"""
    errors = []
    
    required_fields = [
        'taxi_id', 'pickup_location', 'dropoff_location',
        'pickup_latitude', 'pickup_longitude', 
        'dropoff_latitude', 'dropoff_longitude'
    ]
    
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    
    # Validate coordinates
    if 'pickup_latitude' in data and 'pickup_longitude' in data:
        if not validate_coordinates(data['pickup_latitude'], data['pickup_longitude']):
            errors.append('Invalid pickup coordinates')
    
    if 'dropoff_latitude' in data and 'dropoff_longitude' in data:
        if not validate_coordinates(data['dropoff_latitude'], data['dropoff_longitude']):
            errors.append('Invalid dropoff coordinates')
    
    # Validate passenger count
    if 'passenger_count' in data:
        if not isinstance(data['passenger_count'], int) or data['passenger_count'] < 1:
            errors.append('Passenger count must be a positive integer')
    
    # Validate estimated duration
    if 'estimated_duration' in data:
        if not isinstance(data['estimated_duration'], (int, float)) or data['estimated_duration'] <= 0:
            errors.append('Estimated duration must be a positive number')
    
    return errors

def validate_user_data(data):
    """Validate user creation data"""
    errors = []
    
    required_fields = ['username', 'email', 'phone']
    for field in required_fields:
        if field not in data:
            errors.append(f'Missing required field: {field}')
    
    # Validate email format
    if 'email' in data and not validate_email(data['email']):
        errors.append('Invalid email format')
    
    # Validate phone format
    if 'phone' in data and not validate_phone(data['phone']):
        errors.append('Invalid phone number format')
    
    # Validate username
    if 'username' in data:
        if len(data['username']) < 3:
            errors.append('Username must be at least 3 characters long')
        if not data['username'].replace('_', '').isalnum():
            errors.append('Username can only contain letters, numbers, and underscores')
    
    return errors

def calculate_estimated_fare(pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, base_fare=15.0, rate_per_km=8.0):
    """Calculate estimated fare based on distance"""
    import math
    
    # Haversine formula to calculate distance
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1 = math.radians(pickup_lat), math.radians(pickup_lng)
    lat2, lon2 = math.radians(dropoff_lat), math.radians(dropoff_lng)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c  # Distance in kilometers
    
    # Calculate fare
    fare = base_fare + (distance * rate_per_km)
    return round(fare, 2)

def format_response(data, status_code=200, message=None):
    """Format API response"""
    response = {
        'success': status_code < 400,
        'data': data
    }
    
    if message:
        response['message'] = message
    
    return jsonify(response), status_code

