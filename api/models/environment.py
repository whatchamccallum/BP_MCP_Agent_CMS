"""
Environment model for storing test environment information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship

from . import db

class Environment(db.Model):
    """Environment model for storing test environment information."""
    
    __tablename__ = 'environments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(100), nullable=False)
    port = Column(Integer, nullable=False)
    username = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    attributes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    updated_by = Column(String(100), nullable=True)
    
    # Relationships
    test_runs = relationship("TestRun", back_populates="environment")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='uq_environment_name'),
    )
    
    def __repr__(self):
        return f"<Environment(id={self.id}, name='{self.name}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'ip_address': self.ip_address,
            'port': self.port,
            'username': self.username,
            'password': '********',  # Don't return actual password
            'is_active': self.is_active,
            'attributes': self.attributes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }
