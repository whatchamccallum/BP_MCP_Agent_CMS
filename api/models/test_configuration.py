"""
TestConfiguration model for storing test configuration information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from . import db

class TestConfiguration(db.Model):
    """TestConfiguration model for storing test configuration information."""
    
    __tablename__ = 'test_configurations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(String(50), nullable=False)  # e.g., strike, appsim, clientsim, bandwidth
    bp_test_id = Column(String(50), nullable=True)  # Breaking Point test ID, may be null if not yet created
    config_data = Column(JSON, nullable=False)  # Full test configuration
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_runs = relationship("TestRun", back_populates="test_configuration")
    
    def __repr__(self):
        return f"<TestConfiguration(id={self.id}, name='{self.name}', type='{self.test_type}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'test_type': self.test_type,
            'bp_test_id': self.bp_test_id,
            'config_data': self.config_data,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
