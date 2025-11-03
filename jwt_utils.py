"""
JWT utility functions for protecting routes and getting user information
"""

from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from models import User


def require_auth(f):
    """Decorator to require JWT authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        return jwt_required()(f)(*args, **kwargs)
    return decorated_function


def require_role(required_role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {'error': 'User not found'}, 404
            
            # Check role from JWT claims
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role != required_role:
                return {'error': f'Access denied. Required role: {required_role}'}, 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """Get current authenticated user"""
    current_user_id = get_jwt_identity()
    return User.query.get(current_user_id)


def get_user_role():
    """Get current user's role from JWT claims"""
    claims = get_jwt()
    return claims.get('role')


# Example usage in routes:
# 
# @api_bp.route('/admin-only', methods=['GET'])
# @require_role('admin')
# def admin_only_route():
#     return {'message': 'Admin access granted'}
#
# @api_bp.route('/driver-only', methods=['GET'])
# @require_role('driver')
# def driver_only_route():
#     return {'message': 'Driver access granted'}
#
# @api_bp.route('/user-profile', methods=['GET'])
# @require_auth
# def user_profile():
#     user = get_current_user()
#     return {'user': user.to_dict()}




