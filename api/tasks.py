"""
Background tasks for the CMS.
"""

import time
import logging
from celery import Celery
from flask import current_app
from datetime import datetime

from api.models import db
from api.models.test_run import TestRun
from api.controllers.test_controller import TestController

# Configure Celery
def make_celery(app):
    """Create a Celery instance for background tasks."""
    celery = Celery(
        app.import_name,
        backend=app.config.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        broker=app.config.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Create a Celery instance
celery = Celery('bp_mcp_agent_cms')

# Initialize Celery with the Flask app at runtime
@celery.on_after_configure.connect
def setup_celery(sender, **kwargs):
    from app import create_app
    app = create_app()
    celery.conf.update(app.config)


@celery.task
def monitor_test_run(test_run_id):
    """Monitor the status of a test run.
    
    Args:
        test_run_id: ID of the test run to monitor
    """
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Get the test run
        test_run = TestRun.query.get(test_run_id)
        if not test_run:
            app.logger.error(f"Test run {test_run_id} not found")
            return
        
        # Get test controller
        test_controller = TestController()
        
        # Monitor the test until it completes or fails
        while test_run.status == 'running':
            try:
                # Get the current status from Breaking Point
                status = test_controller.get_test_status(test_run)
                
                # If the test has completed or failed, update the status and get results
                if status in ['completed', 'failed']:
                    test_run.status = status
                    test_run.end_time = datetime.utcnow()
                    
                    if test_run.start_time:
                        # Calculate duration in seconds
                        duration = (test_run.end_time - test_run.start_time).total_seconds()
                        test_run.duration = int(duration)
                    
                    db.session.commit()
                    
                    # Get test results
                    try:
                        test_controller.get_test_results(test_run)
                    except Exception as e:
                        app.logger.error(f"Failed to get test results for test run {test_run_id}: {str(e)}")
                    
                    break
            except Exception as e:
                app.logger.error(f"Error monitoring test run {test_run_id}: {str(e)}")
                
                # If there's an error, wait before retrying
                time.sleep(5)
            
            # Wait before checking again
            time.sleep(10)
        
        app.logger.info(f"Test run {test_run_id} monitoring completed with status {test_run.status}")


@celery.task
def cleanup_orphaned_files():
    """Clean up orphaned files in storage."""
    from app import create_app
    app = create_app()
    
    with app.app_context():
        # Get storage
        storage = app.storage
        
        # Get all files in storage
        all_files = storage.list_files("")
        
        # Get all report file paths from the database
        from api.models.report import Report
        report_files = [report.file_path for report in Report.query.all()]
        
        # Get all media file paths from the database
        from api.models.media import Media
        media_files = [media.file_path for media in Media.query.all()]
        
        # Combine all files that should exist
        known_files = report_files + media_files
        
        # Find orphaned files
        orphaned_files = [f for f in all_files if f not in known_files]
        
        # Delete orphaned files
        for file_path in orphaned_files:
            try:
                storage.delete_file(file_path)
                app.logger.info(f"Deleted orphaned file: {file_path}")
            except Exception as e:
                app.logger.error(f"Failed to delete orphaned file {file_path}: {str(e)}")
