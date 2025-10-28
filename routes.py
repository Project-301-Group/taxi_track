from flask import Blueprint, request, jsonify
from models import db, Taxi, Trip, Rank, User
from datetime import datetime, timedelta
from sqlalchemy import func, and_, or_
from utils import handle_errors, validate_trip_data, validate_user_data, format_response

api_bp = Blueprint('api', __name__)

# Rank endpoints
@api_bp.route('/ranks', methods=['GET'])
def get_ranks():
    """Get all taxi ranks with availability information"""
    ranks = Rank.query.all()
    return jsonify([rank.to_dict() for rank in ranks])

@api_bp.route('/ranks/<int:rank_id>', methods=['GET'])
def get_rank(rank_id):
    """Get specific rank details"""
    rank = Rank.query.get_or_404(rank_id)
    return jsonify(rank.to_dict())

@api_bp.route('/ranks/<int:rank_id>/taxis', methods=['GET'])
def get_rank_taxis(rank_id):
    """Get all taxis at a specific rank"""
    taxis = Taxi.query.filter_by(rank_id=rank_id).all()
    return jsonify([taxi.to_dict() for taxi in taxis])

# Taxi endpoints
@api_bp.route('/taxis', methods=['GET'])
def get_taxis():
    """Get all taxis with optional filtering"""
    status = request.args.get('status')
    rank_id = request.args.get('rank_id')
    
    query = Taxi.query
    
    if status:
        query = query.filter_by(status=status)
    if rank_id:
        query = query.filter_by(rank_id=rank_id)
    
    taxis = query.all()
    return jsonify([taxi.to_dict() for taxi in taxis])

@api_bp.route('/taxis/<int:taxi_id>', methods=['GET'])
def get_taxi(taxi_id):
    """Get specific taxi details"""
    taxi = Taxi.query.get_or_404(taxi_id)
    return jsonify(taxi.to_dict())

@api_bp.route('/taxis/<int:taxi_id>/trips', methods=['GET'])
def get_taxi_trips(taxi_id):
    """Get trip history for a specific taxi"""
    trips = Trip.query.filter_by(taxi_id=taxi_id).order_by(Trip.created_at.desc()).all()
    return jsonify([trip.to_dict() for trip in trips])

# Trip endpoints
@api_bp.route('/trips', methods=['GET'])
def get_trips():
    """Get all trips with optional filtering"""
    status = request.args.get('status')
    taxi_id = request.args.get('taxi_id')
    user_id = request.args.get('user_id')
    
    query = Trip.query
    
    if status:
        query = query.filter_by(status=status)
    if taxi_id:
        query = query.filter_by(taxi_id=taxi_id)
    if user_id:
        query = query.filter_by(user_id=user_id)
    
    trips = query.order_by(Trip.created_at.desc()).all()
    return jsonify([trip.to_dict() for trip in trips])

@api_bp.route('/trips', methods=['POST'])
@handle_errors
def create_trip():
    """Create a new trip"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    # Validate trip data
    validation_errors = validate_trip_data(data)
    if validation_errors:
        return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
    
    # Check if taxi is available
    taxi = Taxi.query.get(data['taxi_id'])
    if not taxi:
        return jsonify({'error': 'Taxi not found'}), 404
    
    if taxi.status != 'available':
        return jsonify({'error': 'Taxi is not available'}), 400
    
    # Create trip
    trip = Trip(
        taxi_id=data['taxi_id'],
        user_id=data.get('user_id'),
        pickup_location=data['pickup_location'],
        dropoff_location=data['dropoff_location'],
        pickup_latitude=data['pickup_latitude'],
        pickup_longitude=data['pickup_longitude'],
        dropoff_latitude=data['dropoff_latitude'],
        dropoff_longitude=data['dropoff_longitude'],
        passenger_count=data.get('passenger_count', 1),
        estimated_duration=data.get('estimated_duration', 30)  # Default 30 minutes
    )
    
    # Update taxi status
    taxi.status = 'on_trip'
    
    try:
        db.session.add(trip)
        db.session.commit()
        return format_response(trip.to_dict(), 201, 'Trip created successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@api_bp.route('/trips/<int:trip_id>', methods=['GET'])
def get_trip(trip_id):
    """Get specific trip details"""
    trip = Trip.query.get_or_404(trip_id)
    return jsonify(trip.to_dict())

@api_bp.route('/trips/<int:trip_id>/complete', methods=['PUT'])
def complete_trip(trip_id):
    """Mark a trip as completed"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.status != 'active':
        return jsonify({'error': 'Trip is not active'}), 400
    
    # Calculate actual duration
    if trip.started_at:
        actual_duration = (datetime.utcnow() - trip.started_at).total_seconds() / 60
        trip.actual_duration = actual_duration
    
    trip.status = 'completed'
    trip.completed_at = datetime.utcnow()
    
    # Update taxi status
    trip.taxi.status = 'available'
    
    try:
        db.session.commit()
        return jsonify(trip.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/trips/<int:trip_id>/cancel', methods=['PUT'])
def cancel_trip(trip_id):
    """Cancel a trip"""
    trip = Trip.query.get_or_404(trip_id)
    
    if trip.status != 'active':
        return jsonify({'error': 'Trip is not active'}), 400
    
    trip.status = 'cancelled'
    trip.completed_at = datetime.utcnow()
    
    # Update taxi status
    trip.taxi.status = 'available'
    
    try:
        db.session.commit()
        return jsonify(trip.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Analytics endpoints
@api_bp.route('/analytics/rank/<int:rank_id>', methods=['GET'])
def get_rank_analytics(rank_id):
    """Get analytics for a specific rank"""
    rank = Rank.query.get_or_404(rank_id)
    
    # Get available taxis
    available_taxis = Taxi.query.filter_by(rank_id=rank_id, status='available').count()
    
    # Get active trips from this rank
    active_trips = db.session.query(Trip).join(Taxi).filter(
        Taxi.rank_id == rank_id,
        Trip.status == 'active'
    ).all()
    
    # Calculate estimated completion times
    estimated_completions = []
    for trip in active_trips:
        completion_time = trip.calculate_estimated_completion()
        if completion_time:
            estimated_completions.append({
                'trip_id': trip.id,
                'taxi_id': trip.taxi_id,
                'estimated_completion': completion_time.isoformat(),
                'passenger_count': trip.passenger_count
            })
    
    # Sort by estimated completion time
    estimated_completions.sort(key=lambda x: x['estimated_completion'])
    
    return jsonify({
        'rank_id': rank_id,
        'rank_name': rank.name,
        'available_taxis': available_taxis,
        'total_capacity': rank.max_capacity,
        'active_trips': len(active_trips),
        'estimated_completions': estimated_completions[:5],  # Next 5 expected completions
        'utilization_rate': f"{((rank.max_capacity - available_taxis) / rank.max_capacity * 100):.1f}%"
    })

@api_bp.route('/analytics/daily', methods=['GET'])
def get_daily_analytics():
    """Get daily analytics across all ranks"""
    today = datetime.utcnow().date()
    
    # Get total trips today
    trips_today = Trip.query.filter(
        func.date(Trip.created_at) == today
    ).count()
    
    # Get completed trips today
    completed_today = Trip.query.filter(
        func.date(Trip.completed_at) == today,
        Trip.status == 'completed'
    ).count()
    
    # Get active trips
    active_trips = Trip.query.filter_by(status='active').count()
    
    # Get available taxis
    available_taxis = Taxi.query.filter_by(status='available').count()
    
    # Get total taxis
    total_taxis = Taxi.query.count()
    
    return jsonify({
        'date': today.isoformat(),
        'trips_today': trips_today,
        'completed_today': completed_today,
        'active_trips': active_trips,
        'available_taxis': available_taxis,
        'total_taxis': total_taxis,
        'utilization_rate': f"{((total_taxis - available_taxis) / total_taxis * 100):.1f}%"
    })

# User endpoints
@api_bp.route('/users', methods=['POST'])
@handle_errors
def create_user():
    """Create a new user"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    # Validate user data
    validation_errors = validate_user_data(data)
    if validation_errors:
        return jsonify({'error': 'Validation failed', 'details': validation_errors}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    user = User(
        username=data['username'],
        email=data['email'],
        phone=data['phone']
    )
    
    try:
        db.session.add(user)
        db.session.commit()
        return format_response(user.to_dict(), 201, 'User created successfully')
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user details"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@api_bp.route('/users/<int:user_id>/trips', methods=['GET'])
def get_user_trips(user_id):
    """Get trip history for a specific user"""
    trips = Trip.query.filter_by(user_id=user_id).order_by(Trip.created_at.desc()).all()
    return jsonify([trip.to_dict() for trip in trips])
