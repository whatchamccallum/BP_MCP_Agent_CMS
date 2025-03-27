"""
Database models for the CMS.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import all models to ensure they are registered with SQLAlchemy
from .environment import Environment
from .device import Device
from .test_configuration import TestConfiguration
from .test_run import TestRun
from .test_result import TestResult
from .report import Report
from .media import Media
from .user import User
