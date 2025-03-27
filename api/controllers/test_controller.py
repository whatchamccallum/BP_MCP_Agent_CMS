"""
Test controller for Managing Breaking Point tests.
"""

import os
import sys
from datetime import datetime
from flask import current_app
import json

# Add BP_MCP_Agent to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '..', 'BP_MCP_Agent'))

# Import BP_MCP_Agent modules
from src.api import BreakingPointAPI
from src.analyzer import get_test_result_summary
from src.exceptions import APIError, AuthenticationError, ResourceNotFoundError

from api.models import db
from api.models.test_run import TestRun
from api.models.test_result import TestResult
from api.models.test_configuration import TestConfiguration
from api.models.environment import Environment
from api.models.device import Device


class TestController:
    """Controller for managing Breaking Point tests."""
    
    def __init__(self):
        """Initialize the test controller."""
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
    
    def create_test(self, test_config):
        """Create a test in Breaking Point.
        
        Args:
            test_config: TestConfiguration object
        
        Returns:
            str: Breaking Point test ID
        """
        try:
            self._connect()
            
            # Create the test
            result = self.bp_api.create_test(test_config.config_data)
            
            # Return the test ID
            return result.get('id')
        finally:
            self._disconnect()
    
    def update_test(self, test_config):
        """Update a test in Breaking Point.
        
        Args:
            test_config: TestConfiguration object
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._connect()
            
            # Update the test
            self.bp_api.update_test(test_config.bp_test_id, test_config.config_data)
            
            return True
        except ResourceNotFoundError:
            # If the test doesn't exist, try to create it
            test_config.bp_test_id = self.create_test(test_config)
            db.session.commit()
            return True
        finally:
            self._disconnect()
    
    def delete_test(self, bp_test_id):
        """Delete a test in Breaking Point.
        
        Args:
            bp_test_id: Breaking Point test ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._connect()
            
            # Delete the test
            self.bp_api.delete_test(bp_test_id)
            
            return True
        except ResourceNotFoundError:
            # If the test doesn't exist, just return success
            return True
        finally:
            self._disconnect()
    
    def run_test(self, test_config, environment_id, device_id, created_by=None):
        """Run a test in Breaking Point.
        
        Args:
            test_config: TestConfiguration object
            environment_id: Environment ID
            device_id: Device ID
            created_by: Username of the user who created the test run
        
        Returns:
            TestRun: Created test run object
        """
        # Check if the test configuration exists
        if not isinstance(test_config, TestConfiguration):
            test_config = TestConfiguration.query.get(test_config)
            if not test_config:
                raise ValueError("Test configuration not found")
        
        # Check if the environment exists
        environment = Environment.query.get(environment_id)
        if not environment:
            raise ValueError("Environment not found")
        
        # Check if the device exists
        device = Device.query.get(device_id)
        if not device:
            raise ValueError("Device not found")
        
        # Ensure the test has a BP test ID
        if not test_config.bp_test_id:
            test_config.bp_test_id = self.create_test(test_config)
            db.session.commit()
        
        # Connect to Breaking Point
        self._connect()
        
        try:
            # Run the test
            result = self.bp_api.run_test(test_config.bp_test_id)
            
            # Get the run ID
            bp_run_id = result.get('runId')
            
            if not bp_run_id:
                raise ValueError("Failed to start test: No run ID returned")
            
            # Create the test run
            test_run = TestRun(
                test_config_id=test_config.id,
                environment_id=environment_id,
                device_id=device_id,
                bp_test_id=test_config.bp_test_id,
                bp_run_id=bp_run_id,
                status='running',
                start_time=datetime.utcnow(),
                created_by=created_by
            )
            
            db.session.add(test_run)
            db.session.commit()
            
            # Start a background task to monitor the test
            from api.tasks import monitor_test_run
            monitor_test_run.delay(test_run.id)
            
            return test_run
        finally:
            self._disconnect()
    
    def stop_test(self, test_run):
        """Stop a running test.
        
        Args:
            test_run: TestRun object
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the test run exists
        if not isinstance(test_run, TestRun):
            test_run = TestRun.query.get(test_run)
            if not test_run:
                raise ValueError("Test run not found")
        
        # Only running tests can be stopped
        if test_run.status != 'running':
            raise ValueError("Only running tests can be stopped")
        
        # Connect to Breaking Point
        self._connect()
        
        try:
            # Stop the test
            self.bp_api.stop_test(test_run.bp_test_id)
            
            # Update the test run
            test_run.status = 'stopped'
            test_run.end_time = datetime.utcnow()
            
            if test_run.start_time:
                # Calculate duration in seconds
                duration = (test_run.end_time - test_run.start_time).total_seconds()
                test_run.duration = int(duration)
            
            db.session.commit()
            
            return True
        finally:
            self._disconnect()
    
    def get_test_status(self, test_run):
        """Get the status of a test run.
        
        Args:
            test_run: TestRun object
        
        Returns:
            str: Test status
        """
        # Check if the test run exists
        if not isinstance(test_run, TestRun):
            test_run = TestRun.query.get(test_run)
            if not test_run:
                raise ValueError("Test run not found")
        
        # Connect to Breaking Point
        self._connect()
        
        try:
            # Get the test status
            return self.bp_api.get_test_status(test_run.bp_test_id, test_run.bp_run_id)
        finally:
            self._disconnect()
    
    def get_test_results(self, test_run):
        """Get the results of a test run.
        
        Args:
            test_run: TestRun object
        
        Returns:
            dict: Test results
        """
        # Check if the test run exists
        if not isinstance(test_run, TestRun):
            test_run = TestRun.query.get(test_run)
            if not test_run:
                raise ValueError("Test run not found")
        
        # Connect to Breaking Point
        self._connect()
        
        try:
            # Get the test results
            summary = get_test_result_summary(self.bp_api, test_run.bp_test_id, test_run.bp_run_id)
            
            # Update the test run if needed
            if test_run.status in ['running', 'pending']:
                test_run.status = 'completed'
                test_run.end_time = datetime.utcnow()
                
                if test_run.start_time:
                    # Calculate duration in seconds
                    duration = (test_run.end_time - test_run.start_time).total_seconds()
                    test_run.duration = int(duration)
                
                db.session.commit()
            
            # Check if there's already a test result
            test_result = TestResult.query.filter_by(test_run_id=test_run.id).first()
            
            if test_result:
                # Update the existing test result
                test_result.result_data = summary
                test_result.summary = {
                    'throughput': summary.get('metrics', {}).get('throughput', {}),
                    'latency': summary.get('metrics', {}).get('latency', {}),
                    'strikes': summary.get('metrics', {}).get('strikes', {}),
                    'transactions': summary.get('metrics', {}).get('transactions', {})
                }
            else:
                # Create a new test result
                test_result = TestResult(
                    test_run_id=test_run.id,
                    result_data=summary,
                    summary={
                        'throughput': summary.get('metrics', {}).get('throughput', {}),
                        'latency': summary.get('metrics', {}).get('latency', {}),
                        'strikes': summary.get('metrics', {}).get('strikes', {}),
                        'transactions': summary.get('metrics', {}).get('transactions', {})
                    }
                )
                db.session.add(test_result)
            
            db.session.commit()
            
            return summary
        finally:
            self._disconnect()
