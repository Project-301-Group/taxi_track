from flask import Blueprint, request, jsonify
from models import db, Rank, RankDestination, Trip, Admin, User

rank_dest_bp = Blueprint('rank_dest_bp', __name__)

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
# 1️⃣ Get all ranks except the one managed by this admin
# ------------------------------------------------------------
@rank_dest_bp.route('/ranks/others', methods=['GET'])
def get_other_ranks():
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    admin, admin_rank = get_admin_rank_from_user_id(user_id)
    
    if not admin or not admin_rank:
        return jsonify({"error": "Admin rank not found"}), 404

    current_rank_id = admin_rank.id
    ranks = Rank.query.filter(Rank.id != current_rank_id).all()

    data = [
        {
            "id": rank.id,
            "name": rank.name,
            "city": rank.city,
            "province": rank.province,
            "latitude": rank.latitude,
            "longitude": rank.longitude,
        }
        for rank in ranks
    ]

    
    return jsonify(data), 200


# ------------------------------------------------------------
# 2️⃣ Create a new RankDestination
# ------------------------------------------------------------
@rank_dest_bp.route('/rank_destinations', methods=['POST'])
def create_rank_destination():
    data = request.get_json()
    user_id = data.get("user_id")

    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    admin, rank = get_admin_rank_from_user_id(user_id)

    if not admin or not rank:
        return jsonify({"error": "Admin rank not found"}), 404

    origin_rank_id = rank.id
    destination_rank_id = data.get("destination_rank_id")
    distance_km = data.get("distance_km")
    estimated_duration = data.get("estimated_duration")
    fare = data.get("fare")

    if not destination_rank_id:
        return jsonify({"error": "Destination rank required"}), 400

    # Prevent duplicates
    existing = RankDestination.query.filter_by(
        origin_rank_id=origin_rank_id, destination_rank_id=destination_rank_id
    ).first()
    if existing:
        return jsonify({"error": "Destination already exists"}), 409

    new_dest = RankDestination(
        origin_rank_id=origin_rank_id,
        destination_rank_id=destination_rank_id,
        distance_km=distance_km,
        estimated_duration=estimated_duration,
        fare=fare,
    )
    db.session.add(new_dest)
    db.session.commit()

    return jsonify({"message": "Destination created successfully"}), 201


# ------------------------------------------------------------
# 3️⃣ Toggle activation (activate/deactivate)
# ------------------------------------------------------------
@rank_dest_bp.route('/rank_destinations/<int:id>/toggle', methods=['PUT'])
def toggle_rank_destination(id):
    data = request.get_json() or {}
    user_id = data.get("user_id") or request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    dest = RankDestination.query.get(id)
    if not dest:
        return jsonify({"error": "Destination not found"}), 404

    dest.active = not dest.active
    db.session.commit()

    return jsonify({
        "message": "Destination status updated",
        "active": dest.active
    }), 200


# ------------------------------------------------------------
# 4️⃣ Delete if no trips are associated
# ------------------------------------------------------------
@rank_dest_bp.route('/rank_destinations/<int:id>', methods=['DELETE'])
def delete_rank_destination(id):
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    dest = RankDestination.query.get(id)
    if not dest:
        return jsonify({"error": "Destination not found"}), 404

    # Check for existing trips
    trip_exists = Trip.query.filter_by(rank_destination_id=id).first()
    if trip_exists:
        return jsonify({"error": "Cannot delete; trips exist for this route"}), 400

    db.session.delete(dest)
    db.session.commit()
    return jsonify({"message": "Destination deleted successfully"}), 200


# ------------------------------------------------------------
# 5️⃣ Get all RankDestinations for the admin's rank
# ------------------------------------------------------------
@rank_dest_bp.route('/rank_destinations', methods=['GET'])
def get_rank_destinations():
    user_id = request.args.get('user_id', type=int)
    
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    
    admin, rank = get_admin_rank_from_user_id(user_id)

    if not admin or not rank:
        return jsonify({"error": "Admin rank not found"}), 404

    origin_rank_id = rank.id

    destinations = (
        RankDestination.query
        .filter_by(origin_rank_id=origin_rank_id)
        .join(Rank, RankDestination.destination_rank_id == Rank.id)
        .add_entity(Rank)
        .all()
    )

    data = []
    for dest, destination_rank in destinations:
        data.append({
            "id": dest.id,
            "destination_name": destination_rank.name,
            "city": destination_rank.city,
            "province": destination_rank.province,
            "distance_km": dest.distance_km,
            "estimated_duration": dest.estimated_duration,
            "fare": dest.fare,
            "active": dest.active,
            "created_at": dest.created_at.isoformat()
        })

    return jsonify(data), 200
