"""
Media model for storing information about media files (videos, screenshots, etc.).
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from . import db

class Media(db.Model):
    """Media model for storing information about media files."""
    
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, db.ForeignKey('test_runs.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    media_type = Column(String(50), nullable=False)  # e.g., video, image
    content_type = Column(String(100), nullable=False)  # MIME type
    file_path = Column(String(255), nullable=False)  # Path to the media file
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="media")
    
    def __repr__(self):
        return f"<Media(id={self.id}, name='{self.name}', type='{self.media_type}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'test_run_id': self.test_run_id,
            'name': self.name,
            'description': self.description,
            'media_type': self.media_type,
            'content_type': self.content_type,
            'file_path': self.file_path,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
