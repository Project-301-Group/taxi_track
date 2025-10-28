#!/usr/bin/env python3
"""
Database setup script for Taxi Track application
Run this script to initialize the database with sample data
"""

from app import app
from models import db, Taxi, Trip, Rank, User
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample data for testing"""
    
    # Create sample ranks
    ranks_data = [
        {
            'name': 'Central Station Rank',
            'location': '123 Main Street, Downtown',
            'latitude': -26.2041,
            'longitude': 28.0473,
            'max_capacity': 15
        },
        {
            'name': 'Airport Rank',
            'location': 'Airport Terminal 1',
            'latitude': -26.1332,
            'longitude': 28.2411,
            'max_capacity': 20
        },
        {
            'name': 'Mall Rank',
            'location': '456 Shopping Avenue',
            'latitude': -26.1500,
            'longitude': 28.1000,
            'max_capacity': 10
        }
    ]
    
    ranks = []
    for rank_data in ranks_data:
        rank = Rank(**rank_data)
        db.session.add(rank)
        ranks.append(rank)
    
    db.session.commit()
    
    # Create sample taxis
    taxi_data = [
        {
            'registration_number': 'CA123GP',
            'driver_name': 'John Smith',
            'driver_phone': '+27123456789',
            'capacity': 4,
            'status': 'available',
            'rank_id': ranks[0].id
        },
        {
            'registration_number': 'CA456GP',
            'driver_name': 'Jane Doe',
            'driver_phone': '+27123456790',
            'capacity': 4,
            'status': 'available',
            'rank_id': ranks[0].id
        },
        {
            'registration_number': 'CA789GP',
            'driver_name': 'Mike Johnson',
            'driver_phone': '+27123456791',
            'capacity': 4,
            'status': 'on_trip',
            'rank_id': ranks[1].id
        },
        {
            'registration_number': 'CA101GP',
            'driver_name': 'Sarah Wilson',
            'driver_phone': '+27123456792',
            'capacity': 4,
            'status': 'available',
            'rank_id': ranks[1].id
        },
        {
            'registration_number': 'CA202GP',
            'driver_name': 'David Brown',
            'driver_phone': '+27123456793',
            'capacity': 4,
            'status': 'available',
            'rank_id': ranks[2].id
        }
    ]
    
    taxis = []
    for taxi_info in taxi_data:
        taxi = Taxi(**taxi_info)
        db.session.add(taxi)
        taxis.append(taxi)
    
    db.session.commit()
    
    # Create sample users
    users_data = [
        {
            'username': 'alice_user',
            'email': 'alice@example.com',
            'phone': '+27111111111'
        },
        {
            'username': 'bob_user',
            'email': 'bob@example.com',
            'phone': '+27111111112'
        },
        {
            'username': 'charlie_user',
            'email': 'charlie@example.com',
            'phone': '+27111111113'
        }
    ]
    
    users = []
    for user_info in users_data:
        user = User(**user_info)
        db.session.add(user)
        users.append(user)
    
    db.session.commit()
    
    # Create sample trips
    trips_data = [
        {
            'taxi_id': taxis[2].id,  # Mike Johnson's taxi (on_trip)
            'user_id': users[0].id,
            'pickup_location': 'Airport Terminal 1',
            'dropoff_location': '123 Main Street, Downtown',
            'pickup_latitude': -26.1332,
            'pickup_longitude': 28.2411,
            'dropoff_latitude': -26.2041,
            'dropoff_longitude': 28.0473,
            'passenger_count': 2,
            'status': 'active',
            'estimated_duration': 45,
            'started_at': datetime.utcnow() - timedelta(minutes=15)
        },
        {
            'taxi_id': taxis[0].id,
            'user_id': users[1].id,
            'pickup_location': 'Central Station',
            'dropoff_location': '456 Shopping Avenue',
            'pickup_latitude': -26.2041,
            'pickup_longitude': 28.0473,
            'dropoff_latitude': -26.1500,
            'dropoff_longitude': 28.1000,
            'passenger_count': 1,
            'status': 'completed',
            'estimated_duration': 25,
            'actual_duration': 28,
            'fare': 45.50,
            'started_at': datetime.utcnow() - timedelta(hours=2),
            'completed_at': datetime.utcnow() - timedelta(hours=1, minutes=32)
        }
    ]
    
    for trip_info in trips_data:
        trip = Trip(**trip_info)
        db.session.add(trip)
    
    db.session.commit()
    
    print("Sample data created successfully!")
    print(f"Created {len(ranks)} ranks")
    print(f"Created {len(taxis)} taxis")
    print(f"Created {len(users)} users")
    print(f"Created {len(trips_data)} trips")

def main():
    """Main function to set up database"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")
        
        # Check if data already exists
        if Rank.query.count() == 0:
            create_sample_data()
        else:
            print("Sample data already exists. Skipping data creation.")

if __name__ == '__main__':
    main()
