"""
Device model for storing device under test (DUT) information.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from . import db

class Device(db.Model):
    """Device model for storing device under test (DUT) information."""
    
    __tablename__ = 'devices'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    type = Column(String(50), nullable=False)  # e.g., firewall, router, switch
    ip_address = Column(String(50), nullable=True)
    credentials = Column(JSON, nullable=True)  # Encrypted credentials
    attributes = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_runs = relationship("TestRun", back_populates="device")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('name', name='uq_device_name'),
    )
    
    def __repr__(self):
        return f"<Device(id={self.id}, name='{self.name}', type='{self.type}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'type': self.type,
            'ip_address': self.ip_address,
            'credentials': self.credentials,  # Note: Be careful with sensitive data
            'attributes': self.attributes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
