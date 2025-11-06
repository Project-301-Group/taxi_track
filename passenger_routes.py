from flask import Blueprint, request, jsonify
from models import db, User, Taxi, Trip, Passenger, Rank, RankDestination, trip_passengers
from sqlalchemy import or_

passenger_bp = Blueprint('passenger_bp', __name__)

# ------------------------------------------------------------
# 1️⃣ List all ranks (with optional search by any field)
# ------------------------------------------------------------
@passenger_bp.route('/passenger/ranks', methods=['GET'])
def list_ranks():
    """List all ranks with optional search by name, city, province, or address."""
    search = request.args.get('search', type=str)
    query = Rank.query

    if search:
        like_term = f"%{search}%"
        query = query.filter(
            or_(
                Rank.name.ilike(like_term),
                Rank.city.ilike(like_term),
                Rank.province.ilike(like_term),
                Rank.address.ilike(like_term)
            )
        )

    ranks = query.all()
    if not ranks:
        return jsonify({"message": "No ranks found"}), 404

    data = []
    for rank in ranks:
        data.append({
            "id": rank.id,
            "name": rank.name,
            "address": rank.address,
            "city": rank.city,
            "province": rank.province
        })

    return jsonify({"ranks": data}), 200


# ------------------------------------------------------------
# 2️⃣ List all trips (optional search by destination rank location)
# ------------------------------------------------------------
@passenger_bp.route('/passenger/trips', methods=['GET'])
def list_trips():
    """List all trips; optionally filter by destination location."""
    destination = request.args.get('destination', type=str)

    query = Trip.query.join(RankDestination)
    if destination:
        like_term = f"%{destination}%"
        query = query.join(Rank, RankDestination.destination_rank_id == Rank.id)
        query = query.filter(
            or_(
                Rank.name.ilike(like_term),
                Rank.city.ilike(like_term),
                Rank.province.ilike(like_term)
            )
        )

    trips = query.all()
    if not trips:
        return jsonify({"message": "No trips found"}), 404

    data = []
    for trip in trips:
        rank_dest = trip.rank_destination
        data.append({
            "trip_id": trip.id,
            "status": trip.status,
            "rank_destination": {
                "id": rank_dest.id,
                "destination_name": rank_dest.destination_rank.name if rank_dest.destination_rank else None,
                "distance_km": rank_dest.distance_km,
                "estimated_duration": rank_dest.estimated_duration,
                "fare": rank_dest.fare
            } if rank_dest else None,
            "taxi": {
                "id": trip.taxi.id if trip.taxi else None,
                "registration_number": trip.taxi.registration_number if trip.taxi else None
            }
        })

    return jsonify({"trips": data}), 200


# ------------------------------------------------------------
# 3️⃣ List all destinations (optionally searchable)
# ------------------------------------------------------------
@passenger_bp.route('/passenger/rank/destinations', methods=['GET'])
def list_all_destinations():
    """
    List all rank destinations, optionally filtered by a search term.
    
    Query params:
        search (optional): search text for destination or origin rank names.
    """
    search = request.args.get('search', type=str)

    query = RankDestination.query

    # Optional search by origin or destination name, fare, or distance
    if search:
        search_term = f"%{search}%"
        query = query.join(RankDestination.destination_rank).join(RankDestination.origin_rank).filter(
            db.or_(
                RankDestination.destination_rank.has(name=func.lower(search_term)),
                RankDestination.origin_rank.has(name=func.lower(search_term)),
                func.cast(RankDestination.fare, db.String).ilike(search_term),
                func.cast(RankDestination.distance_km, db.String).ilike(search_term)
            )
        )

    destinations = query.all()
    if not destinations:
        return jsonify({"message": "No destinations found"}), 404

    data = []
    for dest in destinations:
        data.append({
            "id": dest.id,
            "origin_rank": {
                "id": dest.origin_rank.id if dest.origin_rank else None,
                "name": dest.origin_rank.name if dest.origin_rank else None,
                "city": dest.origin_rank.city if hasattr(dest.origin_rank, 'city') else None,
                "province": dest.origin_rank.province if hasattr(dest.origin_rank, 'province') else None
            },
            "destination_rank": {
                "id": dest.destination_rank.id if dest.destination_rank else None,
                "name": dest.destination_rank.name if dest.destination_rank else None,
                "city": dest.destination_rank.city if hasattr(dest.destination_rank, 'city') else None,
                "province": dest.destination_rank.province if hasattr(dest.destination_rank, 'province') else None
            },
            "distance_km": dest.distance_km,
            "estimated_duration": dest.estimated_duration,
            "fare": dest.fare,
            "active": dest.active
        })


    return jsonify({"destinations": data}), 200



# ------------------------------------------------------------
# 4️⃣ List trips either by taxi_id or by rank_destination_id
# ------------------------------------------------------------
@passenger_bp.route('/passenger/trips/filter', methods=['GET'])
def list_filtered_trips():
    """List trips filtered either by taxi_id or rank_destination_id."""
    taxi_id = request.args.get('taxi_id', type=int)
    rank_destination_id = request.args.get('rank_destination_id', type=int)

    if not taxi_id and not rank_destination_id:
        return jsonify({"error": "Provide either taxi_id or rank_destination_id"}), 400

    query = Trip.query
    if taxi_id:
        query = query.filter_by(taxi_id=taxi_id)
    if rank_destination_id:
        query = query.filter_by(rank_destination_id=rank_destination_id)

    trips = query.all()
    if not trips:
        return jsonify({"message": "No trips found for the given filter"}), 404

    data = []
    for trip in trips:
        data.append({
            "trip_id": trip.id,
            "status": trip.status,
            "taxi": {
                "id": trip.taxi.id if trip.taxi else None,
                "registration_number": trip.taxi.registration_number if trip.taxi else None
            },
            "rank_destination": {
                "id": trip.rank_destination.id if trip.rank_destination else None,
                "destination_name": trip.rank_destination.destination_rank.name if trip.rank_destination and trip.rank_destination.destination_rank else None
            }
        })

    return jsonify({"trips": data}), 200


# ------------------------------------------------------------
# 5️⃣ Register passenger to an active trip via taxi registration
# ------------------------------------------------------------
@passenger_bp.route('/passenger/trip/join', methods=['POST'])
def join_trip():
    """Join an active trip using taxi registration and passenger's user_id."""
    data = request.get_json()
    user_id = data.get('user_id')
    registration_number = data.get('registration_number')

    if not user_id or not registration_number:
        return jsonify({"error": "user_id and registration_number are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    taxi = Taxi.query.filter_by(registration_number=registration_number).first()
    if not taxi:
        return jsonify({"error": "Taxi not found"}), 404

    active_trip = Trip.query.filter_by(taxi_id=taxi.id, status="active").first()
    if not active_trip:
        return jsonify({"error": "No active trip found for this taxi"}), 404

    passenger = Passenger.query.filter_by(user_id=user.id).first()
    if not passenger:
        passenger = Passenger(user_id=user.id)
        db.session.add(passenger)
        db.session.flush()

    # Ensure passenger not already on trip
    existing = db.session.query(trip_passengers).filter_by(trip_id=active_trip.id, passenger_id=passenger.id).first()
    if existing:
        return jsonify({"message": "Passenger already part of this trip"}), 200

    # Add to trip
    active_trip.passengers.append(passenger)
    db.session.commit()

    return jsonify({
        "message": "Passenger successfully joined the active trip",
        "trip_id": active_trip.id,
        "taxi_id": taxi.id
    }), 201

# ------------------------------------------------------------
# 6 Get passenger info with trip count
# ------------------------------------------------------------
@passenger_bp.route('/passenger/info', methods=['GET'])
def get_passenger_info():
    """
    Get passenger profile info and total number of trips taken.

    Query params:
        user_id (required): ID of the passenger user
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    passenger = Passenger.query.filter_by(user_id=user_id).first()
    if not passenger or not passenger.user:
        return jsonify({"error": "Passenger not found"}), 404

    # Count trips associated with this passenger
    trip_count = (
        db.session.query(func.count(Trip.id))
        .join(Trip.passengers)
        .filter(Passenger.user_id == user_id)
        .scalar()
    )

    return jsonify({
        "passenger": {
            "id": passenger.id,
            "firstname": passenger.user.firstname,
            "lastname": passenger.user.lastname,
            "phone": passenger.user.phone,
            "address": passenger.address
        },
        "trip_count": trip_count
    }), 200


# ------------------------------------------------------------
# 7 Get passenger's trip list
# ------------------------------------------------------------
@passenger_bp.route('/passenger/trips', methods=['GET'])
def get_passenger_trips():
    """
    Get all trips associated with a given passenger.

    Query params:
        user_id (required): ID of the passenger user
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    passenger = Passenger.query.filter_by(user_id=user_id).first()
    if not passenger:
        return jsonify({"error": "Passenger not found"}), 404

    trips = (
        Trip.query
        .join(Trip.passengers)
        .filter(Passenger.user_id == user_id)
        .all()
    )

    if not trips:
        return jsonify({"message": "No trips found for this passenger"}), 404

    trips_data = []
    for trip in trips:
        rank_dest = trip.rank_destination
        taxi = trip.taxi

        trips_data.append({
            "trip_id": trip.id,
            "status": trip.status,
            "rank_destination": {
                "id": rank_dest.id if rank_dest else None,
                "destination_name": rank_dest.destination_rank.name if rank_dest and rank_dest.destination_rank else None,
                "fare": rank_dest.fare if rank_dest else None,
                "distance_km": rank_dest.distance_km if rank_dest else None,
                "estimated_duration": rank_dest.estimated_duration if rank_dest else None
            } if rank_dest else None,
            "taxi": {
                "id": taxi.id if taxi else None,
                "registration_number": taxi.registration_number if taxi else None
            } if taxi else None
        })

    return jsonify({"passenger_id": passenger.id, "trips": trips_data}), 200
