#!/usr/bin/env python3
"""
Simple test script for the Taxi Track API
Run this after starting the Flask application
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_api():
    """Test the API endpoints"""
    print("Testing Taxi Track API...")
    
    # Test 1: Get all ranks
    print("\n1. Testing GET /ranks")
    try:
        response = requests.get(f"{BASE_URL}/ranks")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            ranks = response.json()
            print(f"Found {len(ranks)} ranks")
            for rank in ranks:
                print(f"  - {rank['name']}: {rank['available_taxis']}/{rank['total_taxis']} taxis available")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 2: Get all taxis
    print("\n2. Testing GET /taxis")
    try:
        response = requests.get(f"{BASE_URL}/taxis")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            taxis = response.json()
            print(f"Found {len(taxis)} taxis")
            for taxi in taxis:
                print(f"  - {taxi['registration_number']}: {taxi['status']} (Driver: {taxi['driver_name']})")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 3: Get active trips
    print("\n3. Testing GET /trips?status=active")
    try:
        response = requests.get(f"{BASE_URL}/trips?status=active")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            trips = response.json()
            print(f"Found {len(trips)} active trips")
            for trip in trips:
                print(f"  - Trip {trip['id']}: {trip['pickup_location']} -> {trip['dropoff_location']}")
                print(f"    Passengers: {trip['passenger_count']}, Status: {trip['status']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 4: Get rank analytics
    print("\n4. Testing GET /analytics/rank/1")
    try:
        response = requests.get(f"{BASE_URL}/analytics/rank/1")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json()
            print(f"Rank: {analytics['rank_name']}")
            print(f"Available taxis: {analytics['available_taxis']}")
            print(f"Active trips: {analytics['active_trips']}")
            print(f"Utilization: {analytics['utilization_rate']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 5: Get daily analytics
    print("\n5. Testing GET /analytics/daily")
    try:
        response = requests.get(f"{BASE_URL}/analytics/daily")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            analytics = response.json()
            print(f"Date: {analytics['date']}")
            print(f"Trips today: {analytics['trips_today']}")
            print(f"Completed today: {analytics['completed_today']}")
            print(f"Active trips: {analytics['active_trips']}")
            print(f"Available taxis: {analytics['available_taxis']}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Test 6: Create a new user
    print("\n6. Testing POST /users")
    try:
        user_data = {
            "username": "test_user",
            "email": "test@example.com",
            "phone": "+27123456789"
        }
        response = requests.post(f"{BASE_URL}/users", json=user_data)
        print(f"Status: {response.status_code}")
        if response.status_code == 201:
            user = response.json()
            print(f"Created user: {user['username']} (ID: {user['id']})")
        else:
            print(f"Error: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nAPI testing completed!")

if __name__ == '__main__':
    test_api()

