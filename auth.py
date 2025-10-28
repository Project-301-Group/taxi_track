from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from models import db, User, Passenger, Driver, Admin


auth_bp = Blueprint('auth', __name__)


def detect_role(user):
    """Determine effective role by checking joined profile tables in priority: passenger, driver, admin."""
    if user.passenger is not None:
        return 'passenger'
    if user.driver is not None:
        return 'driver'
    if user.admin is not None:
        return 'admin'
    return user.role


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login endpoint for passenger/driver/admin using phone. Returns JWT with user id and names.

    Body: { phone: string }
    """
    data = request.get_json(silent=True) or {}
    phone = data.get('phone')

    if not phone:
        return jsonify({'error': 'phone is required'}), 400

    user = User.query.filter_by(phone=phone).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404

    effective_role = detect_role(user)
    
    # Create JWT token with user identity
    additional_claims = {
        'firstname': user.firstname,
        'lastname': user.lastname,
        'role': effective_role
    }
    token = create_access_token(identity=user.id, additional_claims=additional_claims)
    print({
        'token': token,
        'user': {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'phone': user.phone,
            'role': effective_role
        }})

    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'phone': user.phone,
            'role': effective_role
        }
    }), 200


@auth_bp.route('/signup/passenger', methods=['POST'])
def signup_passenger():
    """Create a passenger account and return a JWT.

    Body: {
      firstname, lastname, phone,
      address?, next_of_kin_name?, next_of_kin_relationship?, next_of_kin_phone?
    }
    """
    data = request.get_json(silent=True) or {}

    required = ['firstname', 'lastname', 'phone']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    # Enforce unique phone
    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone already registered'}), 400

    user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phone=data['phone'],
        role='passenger'
    )

    passenger = Passenger(
        user=user,
        address=data.get('address'),
        next_of_kin_name=data.get('next_of_kin_name'),
        next_of_kin_relationship=data.get('next_of_kin_relationship'),
        next_of_kin_phone=data.get('next_of_kin_phone')
    )

    try:
        db.session.add(user)
        db.session.add(passenger)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Create JWT token for new passenger
    additional_claims = {
        'firstname': user.firstname,
        'lastname': user.lastname,
        'role': 'passenger'
    }
    token = create_access_token(identity=user.id, additional_claims=additional_claims)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/signup/driver', methods=['POST'])
def signup_driver():
    """Create a driver account and return a JWT.

    Body: { firstname, lastname, phone, licenseNumber }
    """
    data = request.get_json(silent=True) or {}
    print(data)

    required = ['firstname', 'lastname', 'phone', 'licenseNumber']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': f"Missing required fields: {', '.join(missing)}"}), 400

    if User.query.filter_by(phone=data['phone']).first():
        return jsonify({'error': 'Phone already registered'}), 400

    user = User(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phone=data['phone'],
        role='driver'
    )

    driver = Driver(
        user=user,
        license_number=data['licenseNumber']
    )

    try:
        db.session.add(user)
        db.session.add(driver)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Database error: {str(e)}'}), 500

    # Create JWT token for new driver
    additional_claims = {
        'firstname': user.firstname,
        'lastname': user.lastname,
        'role': 'driver'
    }
    token = create_access_token(identity=user.id, additional_claims=additional_claims)
    
    return jsonify({
        'token': token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    """Example protected route that requires valid JWT"""
    current_user_id = get_jwt_identity()
    
    # Get user from database
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'message': 'This is a protected route',
        'user': {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'phone': user.phone,
            'role': detect_role(user)
        }
    }), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    effective_role = detect_role(user)
    
    return jsonify({
        'user': {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'phone': user.phone,
            'role': effective_role
        }
    }), 200


