"""
Main application entry point for the CMS.
"""

import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from api.models import db
from config import config
from storage import get_storage


def create_app(config_name=None):
    """Create and configure the Flask application."""
    
    # Determine environment
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    
    # Create the Flask app
    app = Flask(__name__, 
              template_folder='web/templates',
              static_folder='web/static',
              static_url_path='/static')
    app.config.from_object(config[config_name])
    
    # Enable CORS
    CORS(app)
    
    # Configure JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers', 'cookies', 'json', 'query_string']
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # For development, enable in production
    app.config['JWT_COOKIE_SECURE'] = False  # For development, set to True in production
    app.config['JWT_SESSION_COOKIE'] = False
    jwt = JWTManager(app)
    
    # Custom JWT handlers
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        # Always convert user identity to string
        return str(user) if user is not None else None
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from api.models import User
        identity = jwt_data["sub"]
        try:
            # Try to convert to int if it's a number in string form
            if identity.isdigit():
                user_id = int(identity)
            else:
                user_id = identity
            return User.query.filter_by(id=user_id).one_or_none()
        except:
            return None
    
    # Add context processor for datetime
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.now()}
    
    # Configure the database
    db.init_app(app)
    
    # Create all database tables
    with app.app_context():
        db.create_all()
    
    # Configure storage
    # Pass all config to get_storage() which will choose relevant parameters
    storage = get_storage(
        storage_type=app.config['STORAGE_TYPE'],
        base_dir=app.config['STORAGE_BASE_DIR'],
        **{k.replace('STORAGE_S3_', '').lower(): v 
           for k, v in app.config.items() if k.startswith('STORAGE_S3_')}
    )
    
    # Add storage to the app context
    app.storage = storage
    
    # Register API blueprints
    from api.routes.environment import environment_blueprint
    from api.routes.device import device_blueprint
    from api.routes.test_configuration import test_configuration_blueprint
    from api.routes.test_run import test_run_blueprint
    from api.routes.report import report_blueprint
    from api.routes.media import media_blueprint
    from api.routes.user import user_blueprint
    from api.routes.auth import auth_blueprint
    
    app.register_blueprint(environment_blueprint, url_prefix='/api/environments')
    app.register_blueprint(device_blueprint, url_prefix='/api/devices')
    app.register_blueprint(test_configuration_blueprint, url_prefix='/api/test-configs')
    app.register_blueprint(test_run_blueprint, url_prefix='/api/test-runs')
    app.register_blueprint(report_blueprint, url_prefix='/api/reports')
    app.register_blueprint(media_blueprint, url_prefix='/api/media')
    app.register_blueprint(user_blueprint, url_prefix='/api/users')
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    
    # Register web blueprints
    from web.views.home import home_blueprint
    from web.views.dashboard import dashboard_blueprint
    
    app.register_blueprint(home_blueprint)
    app.register_blueprint(dashboard_blueprint, url_prefix='/dashboard')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Create a route for checking the API status
    @app.route('/api/status')
    def status():
        return jsonify({'status': 'ok'})
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000)
