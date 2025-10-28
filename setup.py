#!/usr/bin/env python3
"""
Setup script for Taxi Track application
This script helps set up the development environment
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def main():
    """Main setup function"""
    print("Taxi Track API Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"Python version: {sys.version}")
    
    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("Failed to install dependencies. Please check your Python environment.")
        return False
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("\nCreating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost/taxi_track

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=username
MYSQL_PASSWORD=password
MYSQL_DATABASE=taxi_track
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file (please update with your database credentials)")
    
    # Initialize database
    print("\nInitializing database...")
    if not run_command("python database_setup.py", "Setting up database with sample data"):
        print("Warning: Database setup failed. Please check your MySQL connection.")
        print("Make sure MySQL is running and the database credentials are correct.")
    
    print("\n" + "=" * 50)
    print("Setup completed!")
    print("\nNext steps:")
    print("1. Update the .env file with your MySQL credentials")
    print("2. Make sure MySQL is running")
    print("3. Run: python app.py")
    print("4. Test the API with: python test_api.py")
    print("\nAPI will be available at: http://localhost:5000")

if __name__ == '__main__':
    main()

