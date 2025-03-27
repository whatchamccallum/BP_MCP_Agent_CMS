"""
TestRun model for storing test run information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from . import db

class TestRun(db.Model):
    """TestRun model for storing test run information."""
    
    __tablename__ = 'test_runs'
    
    id = Column(Integer, primary_key=True)
    test_config_id = Column(Integer, db.ForeignKey('test_configurations.id'), nullable=False)
    environment_id = Column(Integer, db.ForeignKey('environments.id'), nullable=False)
    device_id = Column(Integer, db.ForeignKey('devices.id'), nullable=False)
    bp_test_id = Column(String(50), nullable=False)  # Breaking Point test ID
    bp_run_id = Column(String(50), nullable=False)   # Breaking Point run ID
    status = Column(String(20), nullable=False)  # e.g., pending, running, completed, failed
    start_time = Column(DateTime, nullable=True)
    end_time = Column(DateTime, nullable=True)
    duration = Column(Integer, nullable=True)  # in seconds
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_configuration = relationship("TestConfiguration", back_populates="test_runs")
    environment = relationship("Environment", back_populates="test_runs")
    device = relationship("Device", back_populates="test_runs")
    test_result = relationship("TestResult", back_populates="test_run", uselist=False)
    reports = relationship("Report", back_populates="test_run")
    media = relationship("Media", back_populates="test_run")
    
    def __repr__(self):
        return f"<TestRun(id={self.id}, bp_test_id='{self.bp_test_id}', bp_run_id='{self.bp_run_id}', status='{self.status}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'test_config_id': self.test_config_id,
            'environment_id': self.environment_id, 
            'device_id': self.device_id,
            'bp_test_id': self.bp_test_id,
            'bp_run_id': self.bp_run_id,
            'status': self.status,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': self.duration,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # Only include relationships if explicitly requested to reduce data size
            # To prevent redundancy and circular references
            **({'test_configuration': self.test_configuration.to_dict()} 
               if hasattr(self, '_include_test_configuration') and self.test_configuration else {}),
            **({'environment': self.environment.to_dict()} 
               if hasattr(self, '_include_environment') and self.environment else {}),
            **({'device': self.device.to_dict()} 
               if hasattr(self, '_include_device') and self.device else {})
        }
