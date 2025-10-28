from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import datetime, timedelta
from sqlalchemy import func
import os
from config import config

from models import db, Taxi, Trip, Rank, User  # Import models here


def create_app():
    app = Flask(__name__)

    # Load configuration
    config_name = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])

    # JWT Configuration
    app.config["JWT_SECRET_KEY"] = app.config.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)  # Tokens expire in 24 hours

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # Import and register blueprints
    from routes import api_bp
    from auth import auth_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route('/')
    def index():
        return jsonify({
            'message': 'Taxi Track API',
            'version': '1.0.0',
            'endpoints': {
                'taxi_ranks': '/api/ranks',
                'taxi_trips': '/api/trips',
                'taxi_status': '/api/taxis',
                'user_trips': '/api/users/<user_id>/trips'
            }
        })

    return app


# This stays for running the API normally
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
