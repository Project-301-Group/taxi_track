from flask import Blueprint, request, jsonify
from models import db, User, Driver, Taxi, Trip, Passenger, RankDestination
import qrcode
import io
import base64
from sqlalchemy import func

driver_bp = Blueprint('driver_bp', __name__)

# ------------------------------------------------------------
# 1️⃣ Get taxi info (including RankDestinations) for logged-in driver
# ------------------------------------------------------------
@driver_bp.route('/driver/taxi', methods=['GET'])
def get_driver_taxi_info():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Get driver and associated user
    driver = Driver.query.filter_by(user_id=user_id).first()
    if not driver or not driver.taxi:
        return jsonify({"error": "Driver or taxi not found"}), 404

    user = driver.user  # Access user profile directly from relationship
    taxi = driver.taxi
    rank = taxi.rank

    # Build rank destinations
    rank_destinations = []
    for rd in rank.destinations:
        rank_destinations.append({
            "id": rd.id,
            "destination_rank_id": rd.destination_rank_id,
            "destination_name": rd.destination_rank.name,
            "distance_km": rd.distance_km,
            "estimated_duration": rd.estimated_duration,
            "fare": rd.fare,
            "active": rd.active
        })

    return jsonify({
        "driver": {
            "id": driver.id,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "phone": user.phone
        },
        "taxi": {
            "id": taxi.id,
            "registration_number": taxi.registration_number,
            "capacity": taxi.capacity,
            "status": taxi.status,
            "rank": {
                "id": rank.id,
                "name": rank.name,
                "address": rank.address,
                "city": rank.city,
                "province": rank.province
            },
            "rank_destinations": rank_destinations
        }
    }), 200


# ------------------------------------------------------------
# 2️⃣ Get total number of trips for the taxi
# ------------------------------------------------------------
@driver_bp.route('/driver/taxi/trips/count', methods=['GET'])
def get_driver_trip_count():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    driver = Driver.query.filter_by(user_id=user_id).first()
    if not driver or not driver.taxi:
        return jsonify({"error": "Driver or taxi not found"}), 404

    trip_count = Trip.query.filter_by(taxi_id=driver.taxi.id).count()
    return jsonify({"taxi_id": driver.taxi.id, "trip_count": trip_count}), 200


# ------------------------------------------------------------
# 3️⃣ Create a new trip and generate QR code
# ------------------------------------------------------------
@driver_bp.route('/driver/trip', methods=['POST'])
def create_trip():
    data = request.get_json()
    user_id = data.get('user_id')
    rank_destination_id = data.get('rank_destination_id')

    if not user_id or not rank_destination_id:
        return jsonify({"error": "user_id and rank_destination_id are required"}), 400

    driver = Driver.query.filter_by(user_id=user_id).first()
    if not driver or not driver.taxi:
        return jsonify({"error": "Driver or taxi not found"}), 404

    # 🚫 Check for existing active trip for this taxi
    active_trip = Trip.query.filter_by(taxi_id=driver.taxi.id, status='active').first()
    if active_trip:
        return jsonify({
            "error": "Cannot create a new trip while there is an active trip.",
            "active_trip_id": active_trip.id
        }), 400

    # ✅ Create a new trip
    new_trip = Trip(
        taxi_id=driver.taxi.id,
        rank_destination_id=rank_destination_id,
        status="active"
    )
    db.session.add(new_trip)
    db.session.commit()

    # Generate QR code for taxi registration number
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(driver.taxi.registration_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return jsonify({
        "trip_id": new_trip.id,
        "taxi_id": driver.taxi.id,
        "qr_code": qr_base64
    }), 201


# ------------------------------------------------------------
# 4️⃣ Handle QR scan from passenger
# ------------------------------------------------------------
@driver_bp.route('/trip/scan', methods=['POST'])
def scan_qr():
    data = request.get_json()
    qr_code_data = data.get('qr_code')
    passenger_info = data.get('passenger')  # dict: firstname, lastname, phone, address (optional)

    if not qr_code_data or not passenger_info:
        return jsonify({"error": "qr_code and passenger info required"}), 400

    # Decode taxi registration number (assume qr_code_data is the registration string)
    taxi = Taxi.query.filter_by(registration_number=qr_code_data).first()
    if not taxi:
        return jsonify({"error": "Taxi not found"}), 404

    # Get active trip
    active_trip = Trip.query.filter_by(taxi_id=taxi.id, status="active").first()
    if not active_trip:
        return jsonify({"error": "Taxi not loading currently"}), 400

    # Create passenger if not exists
    user = User.query.filter_by(phone=passenger_info['phone']).first()
    if not user:
        user = User(
            firstname=passenger_info.get('firstname'),
            lastname=passenger_info.get('lastname'),
            phone=passenger_info.get('phone'),
            role='passenger'
        )
        db.session.add(user)
        db.session.flush()

        passenger = Passenger(user_id=user.id, address=passenger_info.get('address'))
        db.session.add(passenger)
    else:
        passenger = Passenger.query.filter_by(user_id=user.id).first()
        if not passenger:
            passenger = Passenger(user_id=user.id, address=passenger_info.get('address'))
            db.session.add(passenger)

    db.session.flush()

    # Add passenger to trip
    if passenger not in active_trip.passengers:
        active_trip.passengers.append(passenger)

    db.session.commit()

    return jsonify({"message": "Passenger added to trip", "trip_id": active_trip.id}), 200


# ------------------------------------------------------------
# 5️⃣ Get passengers of active trip for a taxi
# ------------------------------------------------------------
@driver_bp.route('/driver/taxi/passengers', methods=['GET'])
def get_active_trip_passengers():
    taxi_id = request.args.get('taxi_id', type=int)
    if not taxi_id:
        return jsonify({"error": "taxi_id is required"}), 400

    taxi = Taxi.query.get(taxi_id)
    if not taxi:
        return jsonify({"error": "Taxi not found"}), 404

    active_trip = Trip.query.filter_by(taxi_id=taxi_id, status="active").first()
    if not active_trip:
        return jsonify({"error": "No active trip found"}), 404

    passengers_data = []
    for passenger in active_trip.passengers:
        if passenger.user:
            passengers_data.append({
                "id": passenger.id,
                "firstname": passenger.user.firstname,
                "lastname": passenger.user.lastname,
                "phone": passenger.user.phone,
                "address": passenger.address
            })

    return jsonify({"trip_id": active_trip.id, "passengers": passengers_data}), 200


# ------------------------------------------------------------
# 6️⃣ Get QR code for driver's active trip
# ------------------------------------------------------------
@driver_bp.route('/driver/trip/qr', methods=['GET'])
def get_active_trip_qr():
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Get driver and their taxi
    driver = Driver.query.filter_by(user_id=user_id).first()
    if not driver or not driver.taxi:
        return jsonify({"error": "Driver or taxi not found"}), 404

    # Find active trip
    active_trip = Trip.query.filter_by(taxi_id=driver.taxi.id, status="active").first()
    if not active_trip:
        return jsonify({"error": "No active trip found for this taxi"}), 404

    # Generate QR code for taxi registration number
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(driver.taxi.registration_number)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    qr_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')

    return jsonify({
        "trip_id": active_trip.id,
        "taxi_id": driver.taxi.id,
        "qr_code": qr_base64
    }), 200


# ------------------------------------------------------------
# 7️⃣ Get all active trips (optionally filtered by driver user_id)
# ------------------------------------------------------------
@driver_bp.route('/driver/trips/active', methods=['GET'])
def get_active_trips():
    user_id = request.args.get('user_id', type=int)

    # Optional: filter by a specific driver's active trip(s)
    if user_id:
        driver = Driver.query.filter_by(user_id=user_id).first()
        if not driver or not driver.taxi:
            return jsonify({"error": "Driver or taxi not found"}), 404

        active_trips = Trip.query.filter_by(taxi_id=driver.taxi.id, status="active").all()
    else:
        # Otherwise return all active trips system-wide
        active_trips = Trip.query.filter_by(status="active").all()

    if not active_trips:
        return jsonify({"message": "No active trips found"}), 404

    trips_data = []
    for trip in active_trips:
        taxi = trip.taxi
        rank_dest = trip.rank_destination
        trips_data.append({
            "trip_id": trip.id,
            "status": trip.status,
            "taxi": {
                "id": taxi.id,
                "registration_number": taxi.registration_number,
                "capacity": taxi.capacity,
                "status": taxi.status
            } if taxi else None,
            "rank_destination": {
                "id": rank_dest.id,
                "destination_name": rank_dest.destination_rank.name if rank_dest and rank_dest.destination_rank else None,
                "fare": rank_dest.fare,
                "distance_km": rank_dest.distance_km,
                "estimated_duration": rank_dest.estimated_duration
            } if rank_dest else None
        })

    return jsonify({"active_trips": trips_data}), 200
