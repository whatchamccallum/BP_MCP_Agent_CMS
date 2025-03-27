"""
Core dashboard views.
"""
from flask import render_template
from api.models.test_run import TestRun
from api.models.test_configuration import TestConfiguration
from api.models.environment import Environment
from api.models.device import Device
from api.models.user import User
from datetime import datetime

from . import dashboard_blueprint

@dashboard_blueprint.route('/')
def index():
    """Dashboard home page."""
    # Get test runs
    test_runs = TestRun.query.order_by(TestRun.created_at.desc()).limit(5).all()
    
    # Get test configs
    test_configs = TestConfiguration.query.order_by(TestConfiguration.created_at.desc()).limit(5).all()
    
    # Get environments
    environments = Environment.query.all()
    
    # Get devices
    devices = Device.query.all()
    
    return render_template(
        'dashboard/index.html',
        test_runs=test_runs,
        test_configs=test_configs,
        environments=environments,
        devices=devices
    )

@dashboard_blueprint.route('/profile')
def profile():
    """User profile page."""
    # Use a default admin user (id=1) for demonstration
    user = User.query.get(1)
    
    if not user:
        # If admin user doesn't exist, create a placeholder
        user = User(
            id=1,
            username="admin",
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            is_admin=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    return render_template(
        'dashboard/profile.html',
        user=user
    )
