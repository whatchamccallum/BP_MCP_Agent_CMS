"""
Dashboard views package.
"""
from flask import Blueprint

# Create the blueprint
dashboard_blueprint = Blueprint('dashboard', __name__)

# Import all views
from .dashboard_core import *
from .test_config_views import *
from .test_run_views import *
from .device_views import *
from .environment_views import *
from .media_views import *
