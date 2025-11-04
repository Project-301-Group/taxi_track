from flask import Blueprint, request, jsonify
from models import db, Taxi, Rank, Admin, User, Driver
from sqlalchemy import or_, func

taxi_bp = Blueprint('taxi_bp', __name__)

# ------------------------------------------------------------
# Helper function to get admin's rank from user_id
# ------------------------------------------------------------
def get_admin_rank_from_user_id(user_id):
    """Get admin's rank from user_id. Returns (admin, rank) or (None, None) if not found."""
    user = User.query.get(user_id)
    if not user:
        return None, None
    
    admin = Admin.query.filter_by(user_id=user_id).first()
    if not admin or not admin.rank:
        return None, None
    
    return admin, admin.rank


# ------------------------------------------------------------
# 1️⃣ List all taxis registered under a rank based on admin's user_id
# ------------------------------------------------------------
@taxi_bp.route('/taxis', methods=['GET'])
def get_taxis_by_rank():
    """Get all taxis registered under the rank managed by the admin.
    
    Query params: user_id (required) - user_id of the admin
    Returns: List of taxis with their details
    """
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Get the rank associated directly with this user_id
    rank = Rank.query.filter_by(admin_id=user_id).first()
    
    if not rank:
        return jsonify({"error": "Rank not found for this user"}), 404

    # Fetch all taxis under this rank
    taxis = Taxi.query.filter_by(rank_id=rank.id).all()

    data = []
    for taxi in taxis:
        taxi_data = {
            "id": taxi.id,
            "registration_number": taxi.registration_number,
            "capacity": taxi.capacity,
            "status": taxi.status,
            "rank_id": taxi.rank_id,
        }

        # Include driver details if available
        if taxi.driver and taxi.driver.user:
            taxi_data["driver"] = {
                "id": taxi.driver.id,
                "firstname": taxi.driver.user.firstname,
                "lastname": taxi.driver.user.lastname,
                "phone": taxi.driver.user.phone,
                "license_number": taxi.driver.license_number,
            }
        else:
            taxi_data["driver"] = None

        data.append(taxi_data)
    
    return jsonify(data), 200


# ------------------------------------------------------------
# 2️⃣ Create a new taxi record
# ------------------------------------------------------------
@taxi_bp.route('/taxis', methods=['POST'])
def create_taxi():
    """Create a new taxi record.
    
    Body: {
        registration_number (required),
        capacity (optional, default 4),
        status (optional, default 'available'),
        user_id (required — linked to admin who manages a rank),
        driver_id (optional)
    }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    registration_number = data.get("registration_number")
    if not registration_number:
        return jsonify({"error": "registration_number is required"}), 400

    # Check for duplicate registration
    existing = Taxi.query.filter_by(registration_number=registration_number).first()
    if existing:
        return jsonify({"error": "Taxi with this registration number already exists"}), 409

    # Get user_id and resolve to rank_id
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    rank = Rank.query.filter_by(admin_id=user_id).first()
    if not rank:
        return jsonify({"error": "No rank found for this user"}), 404

    # Validate driver_id if provided
    driver_id = data.get("driver_id")
    if driver_id:
        driver = Driver.query.get(driver_id)
        if not driver:
            return jsonify({"error": "Driver not found"}), 404

        existing_taxi = Taxi.query.filter_by(driver_id=driver_id).first()
        if existing_taxi:
            return jsonify({"error": "Driver already has a taxi assigned"}), 409

    # Create taxi with inferred rank_id
    new_taxi = Taxi(
        registration_number=registration_number,
        capacity=data.get("capacity", 10),
        status=data.get("status", "available"),
        rank_id=rank.id,
        driver_id=driver_id
    )

    try:
        db.session.add(new_taxi)
        db.session.commit()

        return jsonify({
            "message": "Taxi created successfully",
            "taxi": {
                "id": new_taxi.id,
                "registration_number": new_taxi.registration_number,
                "capacity": new_taxi.capacity,
                "status": new_taxi.status,
                "rank_id": new_taxi.rank_id,
                "driver_id": new_taxi.driver_id
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500


# ------------------------------------------------------------
# 3️⃣ Show all drivers in the system with search by name
# ------------------------------------------------------------
@taxi_bp.route('/drivers', methods=['GET'])
def get_drivers():
    """Get all drivers in the system with optional search by name.
    
    Query params: 
        search (optional) - search by firstname or lastname
    Returns: List of drivers with their details
    """
    search_query = request.args.get('search', '').strip()
    
    # Base query
    query = db.session.query(Driver, User).join(User, Driver.user_id == User.id)
    
    # Apply search filter if provided
    if search_query:
        search_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                User.firstname.ilike(search_pattern),
                User.lastname.ilike(search_pattern),
                func.concat(User.firstname, ' ', User.lastname).ilike(search_pattern)
            )
        )
    
    results = query.all()
    
    data = []
    for driver, user in results:
        driver_data = {
            "id": driver.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "phone": user.phone,
            "license_number": driver.license_number,
            "has_taxi": driver.taxi is not None
        }
        
        # Include taxi information if driver has a taxi
        if driver.taxi:
            driver_data["taxi"] = {
                "id": driver.taxi.id,
                "registration_number": driver.taxi.registration_number,
                "status": driver.taxi.status,
                "rank_id": driver.taxi.rank_id
            }
        else:
            driver_data["taxi"] = None
        
        data.append(driver_data)
        
    
    return jsonify(data), 200

