"""
Breaking Point MCP Agent controller for interacting with the BP MCP Agent.
"""

import os
import sys
import tempfile
from datetime import datetime
import logging

from api.models import db
from api.models.test_run import TestRun
from api.models.test_result import TestResult
from api.models.environment import Environment
from api.models.device import Device

# Configure logger
logger = logging.getLogger(__name__)

class BPAgentController:
    """Controller for interacting with the Breaking Point MCP Agent."""
    
    def __init__(self, app):
        """
        Initialize the controller.
        
        Args:
            app: Flask application with configuration
        """
        self.app = app
        self.bp_mcp_agent_host = app.config.get('BP_MCP_AGENT_HOST')
        self.bp_mcp_agent_port = app.config.get('BP_MCP_AGENT_PORT')
        self.bp_mcp_agent_username = app.config.get('BP_MCP_AGENT_USERNAME')
        self.bp_mcp_agent_password = app.config.get('BP_MCP_AGENT_PASSWORD')
        
        # Add BP MCP Agent to Python path if needed
        bp_mcp_agent_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../BP_MCP_Agent'))
        if os.path.exists(bp_mcp_agent_path) and bp_mcp_agent_path not in sys.path:
            sys.path.append(bp_mcp_agent_path)
        
        # Import BP MCP Agent modules
        try:
            from src.api import BreakingPointAPI
            from src.analyzer import (
                get_test_result_summary,
                generate_report,
                generate_charts,
                get_raw_test_results
            )
            self.BreakingPointAPI = BreakingPointAPI
            self.get_test_result_summary = get_test_result_summary
            self.generate_report_func = generate_report
            self.generate_charts_func = generate_charts
            self.get_raw_test_results = get_raw_test_results
            self.import_success = True
        except ImportError as e:
            logger.error(f"Failed to import BP MCP Agent modules: {e}")
            self.import_success = False
    
    def get_bp_api(self):
        """
        Get a BreakingPointAPI instance.
        
        Returns:
            BreakingPointAPI: Authenticated BP API instance
        
        Raises:
            Exception: If BP MCP Agent modules are not imported or login fails
        """
        if not self.import_success:
            raise Exception("BP MCP Agent modules not imported")
        
        bp_api = self.BreakingPointAPI(
            host=self.bp_mcp_agent_host,
            username=self.bp_mcp_agent_username,
            password=self.bp_mcp_agent_password
        )
        
        if not bp_api.login():
            raise Exception("Failed to log in to Breaking Point")
        
        return bp_api
    
    def run_test(self, test_config, environment_id, device_id, created_by=None):
        """
        Run a test configuration.
        
        Args:
            test_config: TestConfiguration object
            environment_id: Environment ID
            device_id: Device ID
            created_by: User who initiated the test run
        
        Returns:
            TestRun: Created test run object
        
        Raises:
            Exception: If test execution fails
        """
        # Get environment and device
        environment = Environment.query.get(environment_id)
        device = Device.query.get(device_id)
        
        if not environment:
            raise Exception(f"Environment with ID {environment_id} not found")
        
        if not device:
            raise Exception(f"Device with ID {device_id} not found")
        
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            
            # Create test if needed
            bp_test_id = test_config.bp_test_id
            if not bp_test_id:
                # Create the test in BP
                test_result = bp_api.create_test(test_config.config_data)
                bp_test_id = test_result.get('id')
                
                # Update the test config with the BP test ID
                test_config.bp_test_id = bp_test_id
                db.session.commit()
            
            # Run the test
            run_result = bp_api.run_test(bp_test_id)
            bp_run_id = run_result.get('runId')
            
            # Create the test run
            test_run = TestRun(
                test_config_id=test_config.id,
                environment_id=environment.id,
                device_id=device.id,
                bp_test_id=bp_test_id,
                bp_run_id=bp_run_id,
                status='running',
                start_time=datetime.utcnow(),
                created_by=created_by
            )
            
            db.session.add(test_run)
            db.session.commit()
            
            return test_run
            
        finally:
            if bp_api:
                bp_api.logout()
    
    def get_test_status(self, test_run):
        """
        Get the status of a test run.
        
        Args:
            test_run: TestRun object
        
        Returns:
            str: Test status
        
        Raises:
            Exception: If status check fails
        """
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            status = bp_api.get_test_status(test_run.bp_test_id, test_run.bp_run_id)
            
            # Update test run if completed
            if status == 'completed' and test_run.status != 'completed':
                test_run.status = 'completed'
                test_run.end_time = datetime.utcnow()
                
                if test_run.start_time:
                    # Calculate duration in seconds
                    duration = (test_run.end_time - test_run.start_time).total_seconds()
                    test_run.duration = int(duration)
                
                db.session.commit()
            
            return status
            
        finally:
            if bp_api:
                bp_api.logout()
    
    def stop_test(self, test_run):
        """
        Stop a running test.
        
        Args:
            test_run: TestRun object
        
        Raises:
            Exception: If test stop fails
        """
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            bp_api.stop_test(test_run.bp_test_id)
            
            # Update test run
            test_run.status = 'stopped'
            test_run.end_time = datetime.utcnow()
            
            if test_run.start_time:
                # Calculate duration in seconds
                duration = (test_run.end_time - test_run.start_time).total_seconds()
                test_run.duration = int(duration)
            
            db.session.commit()
            
        finally:
            if bp_api:
                bp_api.logout()
    
    def get_test_results(self, test_run):
        """
        Get test results.
        
        Args:
            test_run: TestRun object
        
        Returns:
            dict: Test results
        
        Raises:
            Exception: If results retrieval fails
        """
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            results = self.get_raw_test_results(bp_api, test_run.bp_test_id, test_run.bp_run_id)
            return results
            
        finally:
            if bp_api:
                bp_api.logout()
    
    def extract_result_summary(self, results):
        """
        Extract a summary from test results.
        
        Args:
            results: Raw test results
        
        Returns:
            dict: Summary of test results
        """
        summary = {}
        
        # Extract basic metrics
        if 'metrics' in results:
            metrics = results['metrics']
            
            summary['throughput'] = metrics.get('throughput', {})
            summary['latency'] = metrics.get('latency', {})
            summary['strikes'] = metrics.get('strikes', {})
            summary['transactions'] = metrics.get('transactions', {})
        
        return summary
    
    def generate_report(self, test_run, report_type, file_format):
        """
        Generate a report for a test run.
        
        Args:
            test_run: TestRun object
            report_type: Report type (standard, executive, detailed, compliance)
            file_format: File format (html, pdf, csv)
        
        Returns:
            tuple: (report_path, report_filename)
        
        Raises:
            Exception: If report generation fails
        """
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            
            # Create a temporary directory for the report
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate the report
                report_path = self.generate_report_func(
                    bp_api,
                    test_run.bp_test_id,
                    test_run.bp_run_id,
                    file_format,
                    report_type,
                    temp_dir
                )
                
                # Get the report filename
                report_filename = os.path.basename(report_path)
                
                # Get the storage
                storage = self.app.storage
                
                # Create the storage path
                storage_path = f"reports/{test_run.id}/{report_filename}"
                
                # Store the report
                with open(report_path, 'rb') as f:
                    stored_path = storage.save_file(f, storage_path)
                
                return stored_path, report_filename
                
        finally:
            if bp_api:
                bp_api.logout()
    
    def generate_charts(self, test_run, output_dir=None):
        """
        Generate charts for a test run.
        
        Args:
            test_run: TestRun object
            output_dir: Output directory
        
        Returns:
            list: Paths to generated chart files
        
        Raises:
            Exception: If chart generation fails
        """
        bp_api = None
        try:
            bp_api = self.get_bp_api()
            
            # Create a temporary directory for the charts
            with tempfile.TemporaryDirectory() as temp_dir:
                # Generate the charts
                chart_paths = self.generate_charts_func(
                    bp_api,
                    test_run.bp_test_id,
                    test_run.bp_run_id,
                    temp_dir
                )
                
                # Get the storage
                storage = self.app.storage
                
                # Store the charts
                stored_paths = []
                for chart_path in chart_paths:
                    # Get the chart filename
                    chart_filename = os.path.basename(chart_path)
                    
                    # Create the storage path
                    storage_path = f"charts/{test_run.id}/{chart_filename}"
                    
                    # Store the chart
                    with open(chart_path, 'rb') as f:
                        stored_path = storage.save_file(f, storage_path)
                    
                    stored_paths.append(stored_path)
                
                return stored_paths
                
        finally:
            if bp_api:
                bp_api.logout()
