"""
Report model for storing information about generated reports.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from . import db

class Report(db.Model):
    """Report model for storing information about generated reports."""
    
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    test_run_id = Column(Integer, db.ForeignKey('test_runs.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    report_type = Column(String(50), nullable=False)  # e.g., standard, executive, detailed, compliance
    file_format = Column(String(20), nullable=False)  # e.g., html, pdf, csv
    file_path = Column(String(255), nullable=False)   # Path to the report file
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    test_run = relationship("TestRun", back_populates="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, name='{self.name}', type='{self.report_type}', format='{self.file_format}')>"
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'test_run_id': self.test_run_id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type,
            'file_format': self.file_format,
            'file_path': self.file_path,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
