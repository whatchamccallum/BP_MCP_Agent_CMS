"""
Integration with the Breaking Point MCP Agent.
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger("BPAgent.Integration")


class BPMCPAgentClient:
    """Client for interacting with the Breaking Point MCP Agent."""
    
    def __init__(self, host: str, port: int, username: str, password: str):
        """
        Initialize the Breaking Point MCP Agent client.
        
        Args:
            host: Breaking Point MCP Agent host
            port: Breaking Point MCP Agent port
            username: Breaking Point MCP Agent username
            password: Breaking Point MCP Agent password
        """
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.base_url = f"http://{host}:{port}"
        
    def get_test_result_summary(self, test_id: str, run_id: str) -> Dict:
        """
        Get a summary of test results.
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            Dict: Test result summary
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/analyzer/summary"
        
        data = {
            "test_id": test_id,
            "run_id": run_id,
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def generate_report(self, test_id: str, run_id: str, report_type: str, output_format: str) -> Tuple[bytes, str]:
        """
        Generate a report for a test run.
        
        Args:
            test_id: Test ID
            run_id: Run ID
            report_type: Report type (standard, executive, detailed, compliance)
            output_format: Output format (html, pdf, csv)
            
        Returns:
            Tuple[bytes, str]: Report data and file extension
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/analyzer/report"
        
        data = {
            "test_id": test_id,
            "run_id": run_id,
            "report_type": report_type,
            "output_format": output_format,
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        # Get the Content-Disposition header to extract the filename
        content_disposition = response.headers.get('Content-Disposition', '')
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[1].strip('"\'')
            _, ext = os.path.splitext(filename)
            ext = ext.lstrip('.')
        else:
            ext = output_format
        
        return response.content, ext
    
    def generate_charts(self, test_id: str, run_id: str) -> List[Tuple[bytes, str]]:
        """
        Generate charts for test results.
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            List[Tuple[bytes, str]]: List of chart data and filenames
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/analyzer/charts"
        
        data = {
            "test_id": test_id,
            "run_id": run_id,
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        # The response should be a ZIP file containing the charts
        # For now, we'll assume the agent returns a list of charts in the response
        charts = response.json()
        
        result = []
        for chart in charts:
            chart_url = chart['url']
            chart_response = requests.get(chart_url)
            chart_response.raise_for_status()
            
            filename = os.path.basename(chart_url)
            result.append((chart_response.content, filename))
        
        return result
    
    def run_test(self, config_data: Dict) -> Dict:
        """
        Run a test with the given configuration.
        
        Args:
            config_data: Test configuration data
            
        Returns:
            Dict: Test run information
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/test/run"
        
        # Add credentials to the configuration
        data = config_data.copy()
        data["username"] = self.username
        data["password"] = self.password
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def stop_test(self, test_id: str, run_id: str) -> Dict:
        """
        Stop a running test.
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            Dict: Result of the stop operation
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/test/stop"
        
        data = {
            "test_id": test_id,
            "run_id": run_id,
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_test_status(self, test_id: str, run_id: str) -> str:
        """
        Get the status of a test run.
        
        Args:
            test_id: Test ID
            run_id: Run ID
            
        Returns:
            str: Test status
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}/test/status"
        
        data = {
            "test_id": test_id,
            "run_id": run_id,
            "username": self.username,
            "password": self.password
        }
        
        response = requests.post(url, json=data)
        response.raise_for_status()
        
        return response.json().get("status", "unknown")
