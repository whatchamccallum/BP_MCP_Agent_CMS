"""
Report controller for generating Breaking Point reports.
"""

import os
import sys
from datetime import datetime
from flask import current_app
import json
import uuid

# Add BP_MCP_Agent to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..', 'BP_MCP_Agent'))

# Import BP_MCP_Agent modules
from src.api import BreakingPointAPI
from src.analyzer import generate_report as bp_generate_report
from src.exceptions import APIError, AuthenticationError, ResourceNotFoundError, ReportError

from api.models import db
from api.models.test_run import TestRun
from api.models.report import Report


class ReportController:
    """Controller for generating Breaking Point reports."""
    
    def __init__(self):
        """Initialize the report controller."""
        self.host = current_app.config['BP_MCP_AGENT_HOST']
        self.username = current_app.config['BP_MCP_AGENT_USERNAME']
        self.password = current_app.config['BP_MCP_AGENT_PASSWORD']
        self.bp_api = None
    
    def _connect(self):
        """Connect to Breaking Point API."""
        if not self.bp_api:
            self.bp_api = BreakingPointAPI(self.host, self.username, self.password)
            self.bp_api.login()
    
    def _disconnect(self):
        """Disconnect from Breaking Point API."""
        if self.bp_api:
            self.bp_api.logout()
            self.bp_api = None
    
    def generate_report(self, test_run, report_type, file_format, name=None, description=None, created_by=None):
        """Generate a report for a test run.
        
        Args:
            test_run: TestRun object
            report_type: Report type (standard, executive, detailed, compliance)
            file_format: File format (html, pdf, csv)
            name: Report name (optional)
            description: Report description (optional)
            created_by: Username of the user who created the report (optional)
        
        Returns:
            Report: Generated report object
        """
        # Check if the test run exists
        if not isinstance(test_run, TestRun):
            test_run = TestRun.query.get(test_run)
            if not test_run:
                raise ValueError("Test run not found")
        
        # Only completed tests can have reports generated
        if test_run.status not in ['completed', 'failed', 'stopped']:
            raise ValueError("Cannot generate report for a test that has not completed")
        
        # Validate report type
        valid_report_types = ['standard', 'executive', 'detailed', 'compliance']
        if report_type not in valid_report_types:
            raise ValueError(f"Invalid report type. Must be one of: {', '.join(valid_report_types)}")
        
        # Validate file format
        valid_file_formats = ['html', 'pdf', 'csv']
        if file_format not in valid_file_formats:
            raise ValueError(f"Invalid file format. Must be one of: {', '.join(valid_file_formats)}")
        
        # Set up report name if not provided
        if not name:
            name = f"{test_run.test_configuration.name} - {report_type.capitalize()} Report"
        
        # Generate a unique report directory
        report_dir = os.path.join(current_app.config['STORAGE_BASE_DIR'], 'reports', str(test_run.id))
        os.makedirs(report_dir, exist_ok=True)
        
        # Connect to Breaking Point
        self._connect()
        
        try:
            # Generate the report
            report_path = bp_generate_report(
                self.bp_api,
                test_run.bp_test_id,
                test_run.bp_run_id,
                file_format,
                report_type,
                report_dir
            )
            
            # Get the relative path within storage
            storage_path = os.path.relpath(report_path, current_app.config['STORAGE_BASE_DIR'])
            
            # Create the report record
            report = Report(
                test_run_id=test_run.id,
                name=name,
                description=description,
                report_type=report_type,
                file_format=file_format,
                file_path=storage_path,
                created_by=created_by
            )
            
            db.session.add(report)
            db.session.commit()
            
            return report
        except ReportError as e:
            raise ValueError(f"Failed to generate report: {str(e)}")
        finally:
            self._disconnect()
