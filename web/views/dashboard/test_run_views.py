"""
Test run views.
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from api.models import db
from api.models.test_run import TestRun
from api.models.test_configuration import TestConfiguration
from api.models.environment import Environment
from api.models.device import Device
from api.models.report import Report
from api.models.media import Media
from datetime import datetime

from .utils import get_current_user, normalize_user_id
from . import dashboard_blueprint

@dashboard_blueprint.route('/test-runs')
def test_runs():
    """Test runs page."""
    # Get test runs
    test_runs = TestRun.query.order_by(TestRun.created_at.desc()).all()
    
    return render_template(
        'dashboard/test_runs.html',
        test_runs=test_runs
    )

@dashboard_blueprint.route('/test-runs/<int:id>')
def test_run_detail(id):
    """Test run detail page."""
    # Get test run
    test_run = TestRun.query.get_or_404(id)
    
    # Get reports
    reports = Report.query.filter_by(test_run_id=id).all()
    
    # Get media
    media_files = Media.query.filter_by(test_run_id=id).all()
    
    return render_template(
        'dashboard/test_run_detail.html',
        test_run=test_run,
        reports=reports,
        media_files=media_files
    )

@dashboard_blueprint.route('/test-runs/create', methods=['POST'])
def run_test():
    """Create a new test run from a test configuration."""
    try:
        # Get current user
        current_user = get_current_user()
        
        test_config_id = request.form.get('test_config_id')
        environment_id = request.form.get('environment_id')
        device_id = request.form.get('device_id')
        
        if not test_config_id or not environment_id or not device_id:
            flash('Test configuration, environment, and device are required', 'error')
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            return redirect(url_for('dashboard.test_configs'))
        
        # Get test configuration, environment, and device
        test_config = TestConfiguration.query.get_or_404(test_config_id)
        environment = Environment.query.get_or_404(environment_id)
        device = Device.query.get_or_404(device_id)
        
        # Create test run
        test_run = TestRun(
            test_config_id=test_config.id,
            environment_id=environment.id,
            device_id=device.id,
            status='scheduled',
            created_by=normalize_user_id(current_user)
        )
        
        db.session.add(test_run)
        db.session.commit()
        
        # TODO: Implement actual test execution logic
        
        flash('Test run created successfully', 'success')
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.test_run_detail', id=test_run.id)
            })
        
        return redirect(url_for('dashboard.test_run_detail', id=test_run.id))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error creating test run: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.test_configs'))

@dashboard_blueprint.route('/test-runs/<int:id>/stop', methods=['POST'])
def stop_test_run(id):
    """Stop a running test run."""
    try:
        # Get current user
        current_user = normalize_user_id(get_current_user())
        
        test_run = TestRun.query.get_or_404(id)
        
        if test_run.status != 'running':
            flash('Test run is not currently running', 'error')
            if request.is_json:
                return jsonify({'error': 'Test run is not currently running'}), 400
            return redirect(url_for('dashboard.test_run_detail', id=id))
        
        test_run.status = 'stopped'
        test_run.end_time = datetime.utcnow()
        test_run.updated_by = current_user
        
        db.session.commit()
        
        flash('Test run stopped successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.test_run_detail', id=id)
            })
        
        return redirect(url_for('dashboard.test_run_detail', id=id))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error stopping test run: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.test_run_detail', id=id))

@dashboard_blueprint.route('/reports')
def reports():
    """Reports page."""
    # Get reports
    reports = Report.query.order_by(Report.created_at.desc()).all()
    
    return render_template(
        'dashboard/reports.html',
        reports=reports
    )
