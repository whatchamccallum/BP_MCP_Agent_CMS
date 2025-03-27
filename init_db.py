"""
Database initialization script.
"""

import os
import sys
from flask import Flask
from api.models import db
from config import config


def create_app(config_name=None):
    """Create the Flask application."""
    # Determine environment
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    
    # Create a minimal Flask app for database init
    app = Flask(__name__, static_folder=None, template_folder=None)
    app.config.from_object(config[config_name])
    
    # Configure the database
    db.init_app(app)
    
    return app


def init_db():
    """Initialize the database."""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        from api.models.user import User
        
        # Check if the admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                is_admin=True
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'admin'")
        else:
            print("Admin user already exists")
        
        print("Database initialized successfully")


if __name__ == '__main__':
    init_db()
