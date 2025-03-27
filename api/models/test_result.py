"""
TestResult model for storing test result data.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from . import db

class TestResult(db.Model):
    """TestResult model for storing test result data."""
    
    __tablename__ = 'test_results'
    
    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, db.ForeignKey('test_runs.id'), nullable=False)
    result_data = Column(JSON, nullable=True)  # Full test results
    summary = Column(JSON, nullable=True)      # Summary metrics
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="test_result")
    
    def __repr__(self):
        return f'<TestResult {self.id}>'
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'test_run_id': self.test_run_id,
            'result_data': self.result_data,
            'summary': self.summary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
