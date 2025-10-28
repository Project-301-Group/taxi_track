from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ===============================================================
# Base User model (shared fields)
# ===============================================================

class User(db.Model):
    """Base user account for all system users."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(100), nullable=False)
    lastname = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'driver', 'passenger'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One-to-one relationships to specialized profiles
    driver = db.relationship('Driver', back_populates='user', uselist=False)
    passenger = db.relationship('Passenger', back_populates='user', uselist=False)
    admin = db.relationship('Admin', back_populates='user', uselist=False)

    def to_dict(self):
        return {
            'id': self.id,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'phone': self.phone,
            'role': self.role
        }

# ===============================================================
# Specialized User Roles
# ===============================================================

class Driver(db.Model):
    """Driver profile extending base User."""
    __tablename__ = 'drivers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    user = db.relationship('User', back_populates='driver')

    # Relationship: One driver has one taxi
    taxi = db.relationship('Taxi', back_populates='driver', uselist=False)


class Passenger(db.Model):
    """Passenger profile extending base User."""
    __tablename__ = 'passengers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    address = db.Column(db.String(200))
    next_of_kin_name = db.Column(db.String(100))
    next_of_kin_relationship = db.Column(db.String(50))
    next_of_kin_phone = db.Column(db.String(20))
    user = db.relationship('User', back_populates='passenger')

    # Many-to-many relationship with Trip (passenger <-> trips)
    trips = db.relationship('Trip', secondary='trip_passengers', back_populates='passengers')


class Admin(db.Model):
    """Admin profile extending base User."""
    __tablename__ = 'admins'

    id = db.Column(db.Integer, primary_key=True)
    rank = db.relationship('Rank', back_populates='admin', uselist=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    user = db.relationship('User', back_populates='admin')

# ===============================================================
# Taxi and Rank Models
# ===============================================================

class Rank(db.Model):
    """Taxi rank (pickup/drop-off stations)."""
    __tablename__ = 'ranks'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # e.g. "Warwick Junction Rank"
    address = db.Column(db.String(200), nullable=False)  # full street address
    city = db.Column(db.String(100), nullable=False)  # e.g. "Durban"
    province = db.Column(db.String(100), nullable=False)  # e.g. "KwaZulu-Natal"
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    max_capacity = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), unique=True, nullable=False)
    admin = db.relationship('Admin', back_populates='rank')

    taxis = db.relationship('Taxi', backref='rank', lazy=True)

    # Fixed relationships for self-bridge
    destinations = db.relationship(
        'RankDestination',
        back_populates='origin_rank',
        foreign_keys='RankDestination.origin_rank_id',
        lazy=True
    )
    incoming_routes = db.relationship(
        'RankDestination',
        back_populates='destination_rank',
        foreign_keys='RankDestination.destination_rank_id',
        lazy=True
    )


class RankDestination(db.Model):
    """Represents destinations available *from* a given rank."""
    __tablename__ = 'rank_destinations'

    id = db.Column(db.Integer, primary_key=True)
    origin_rank_id = db.Column(db.Integer, db.ForeignKey('ranks.id'), nullable=False)
    destination_rank_id = db.Column(db.Integer, db.ForeignKey('ranks.id'), nullable=False)
    distance_km = db.Column(db.Float)
    estimated_duration = db.Column(db.Integer)  # in minutes
    fare = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Fixed relationships
    origin_rank = db.relationship(
        'Rank',
        foreign_keys=[origin_rank_id],
        back_populates='destinations'
    )
    destination_rank = db.relationship(
        'Rank',
        foreign_keys=[destination_rank_id],
        back_populates='incoming_routes'
    )

class Taxi(db.Model):
    """Taxi vehicle."""
    __tablename__ = 'taxis'

    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(20), unique=True, nullable=False)
    capacity = db.Column(db.Integer, default=4)
    status = db.Column(db.String(20), default='available')  # available, on_trip, offline
    rank_id = db.Column(db.Integer, db.ForeignKey('ranks.id'))
    driver_id = db.Column(db.Integer, db.ForeignKey('drivers.id'), unique=True)  # 1-to-1

    driver = db.relationship('Driver', back_populates='taxi')
    trips = db.relationship('Trip', backref='taxi', lazy=True)


# Many-to-many bridge table (Trip <-> Passengers)
trip_passengers = db.Table('trip_passengers',
    db.Column('trip_id', db.Integer, db.ForeignKey('trips.id'), primary_key=True),
    db.Column('passenger_id', db.Integer, db.ForeignKey('passengers.id'), primary_key=True)
)

class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    taxi_id = db.Column(db.Integer, db.ForeignKey('taxis.id'), nullable=False)
    rank_destination_id = db.Column(db.Integer, db.ForeignKey('rank_destinations.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, completed, cancelled
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    passengers = db.relationship('Passenger', secondary='trip_passengers', back_populates='trips')
    rank_destination = db.relationship('RankDestination')

# ===============================================================
# End of Models
# ===============================================================
