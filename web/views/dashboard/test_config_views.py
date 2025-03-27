"""
Test configuration views.
"""
import json
from flask import render_template, redirect, url_for, request, flash, jsonify
from api.models import db
from api.models.test_configuration import TestConfiguration
from api.models.test_run import TestRun
from api.models.environment import Environment
from api.models.device import Device
from datetime import datetime

from .utils import get_current_user, normalize_user_id
from . import dashboard_blueprint

@dashboard_blueprint.route('/test-configs/check-name', methods=['GET'])
def check_test_config_name():
    """Check if a test configuration name already exists."""
    name = request.args.get('name')
    config_id = request.args.get('id')
    
    if not name:
        return jsonify({'valid': False, 'message': 'Test configuration name is required'})
    
    query = TestConfiguration.query.filter(TestConfiguration.name == name)
    if config_id:
        # If updating, exclude the current configuration from the check
        query = query.filter(TestConfiguration.id != int(config_id))
    
    exists = query.first() is not None
    
    return jsonify({
        'valid': not exists,
        'message': f'A test configuration with the name "{name}" already exists' if exists else ''
    })

@dashboard_blueprint.route('/test-configs')
def test_configs():
    """Test configurations page."""
    # Get test configurations
    test_configs = TestConfiguration.query.order_by(TestConfiguration.created_at.desc()).all()
    
    return render_template(
        'dashboard/test_configs.html',
        test_configs=test_configs
    )

@dashboard_blueprint.route('/test-configs/<int:id>')
def test_config_detail(id):
    """Test configuration detail page."""
    # Get test configuration
    test_config = TestConfiguration.query.get_or_404(id)
    
    # Get environments
    environments = Environment.query.all()
    
    # Get devices
    devices = Device.query.all()
    
    return render_template(
        'dashboard/test_config_detail.html',
        test_config=test_config,
        environments=environments,
        devices=devices
    )

@dashboard_blueprint.route('/test-configs/create', methods=['POST'])
def create_test_config():
    """Create a new test configuration."""
    try:
        # Get current user
        current_user = get_current_user()
        
        name = request.form.get('name')
        test_type = request.form.get('test_type')
        description = request.form.get('description')
        
        if not name or not test_type:
            flash('Name and test type are required', 'error')
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            return redirect(url_for('dashboard.test_configs'))
        
        # Check if name already exists
        existing_config = TestConfiguration.query.filter_by(name=name).first()
        if existing_config:
            flash(f'A test configuration with the name "{name}" already exists', 'error')
            if request.is_json:
                return jsonify({'error': f'A test configuration with the name "{name}" already exists'}), 400
            return redirect(url_for('dashboard.test_configs'))
        
        # Create default configuration JSON
        config_data = {
            "test_type": test_type,
            "parameters": {},
            "settings": {}
        }
        
        test_config = TestConfiguration(
            name=name,
            test_type=test_type,
            description=description,
            config_data=config_data,
            created_by=normalize_user_id(current_user)
        )
        
        db.session.add(test_config)
        db.session.commit()
        
        flash('Test configuration created successfully', 'success')
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.test_configs')
            })
        
        return redirect(url_for('dashboard.test_configs'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error creating test configuration: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.test_configs'))

@dashboard_blueprint.route('/test-configs/<int:id>/update', methods=['POST'])
def update_test_config(id):
    """Update an existing test configuration."""
    try:
        # Get current user
        current_user = get_current_user()
        
        # Get test configuration
        test_config = TestConfiguration.query.get_or_404(id)
        
        name = request.form.get('name')
        test_type = request.form.get('test_type')
        description = request.form.get('description')
        configuration_json = request.form.get('configuration')
        
        if not name or not test_type:
            flash('Name and test type are required', 'error')
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            return redirect(url_for('dashboard.test_config_detail', id=id))
        
        # Check if name already exists (excluding this config)
        name_conflict = TestConfiguration.query.filter(
            TestConfiguration.name == name, 
            TestConfiguration.id != id
        ).first()
        
        if name_conflict:
            flash(f'Another test configuration with the name "{name}" already exists', 'error')
            if request.is_json:
                return jsonify({'error': f'Another test configuration with the name "{name}" already exists'}), 400
            return redirect(url_for('dashboard.test_config_detail', id=id))
        
        # Update configuration JSON
        try:
            if configuration_json:
                config_data = json.loads(configuration_json)
            else:
                config_data = test_config.config_data
                
            # Update the test_type in configuration
            if isinstance(config_data, dict) and 'test_type' in config_data:
                config_data['test_type'] = test_type
        except json.JSONDecodeError:
            flash('Invalid JSON configuration format', 'error')
            if request.is_json:
                return jsonify({'error': 'Invalid JSON configuration format'}), 400
            return redirect(url_for('dashboard.test_config_detail', id=id))
        
        # Update test configuration
        test_config.name = name
        test_config.test_type = test_type
        test_config.description = description
        test_config.config_data = config_data
        test_config.updated_at = datetime.utcnow()
        test_config.updated_by = normalize_user_id(current_user)
        
        db.session.commit()
        
        flash('Test configuration updated successfully', 'success')
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.test_config_detail', id=id)
            })
        
        return redirect(url_for('dashboard.test_config_detail', id=id))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating test configuration: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.test_config_detail', id=id))

@dashboard_blueprint.route('/test-configs/<int:id>/delete', methods=['POST'])
def delete_test_config(id):
    """Delete an existing test configuration."""
    try:
        # Get test configuration
        test_config = TestConfiguration.query.get_or_404(id)
        
        # Check if there are any test runs using this configuration
        test_runs = TestRun.query.filter_by(test_config_id=id).first()
        if test_runs:
            flash('Cannot delete test configuration that has associated test runs', 'error')
            if request.is_json:
                return jsonify({'error': 'Cannot delete test configuration that has associated test runs'}), 400
            return redirect(url_for('dashboard.test_configs'))
        
        # Delete test configuration
        db.session.delete(test_config)
        db.session.commit()
        
        flash('Test configuration deleted successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.test_configs')
            })
        
        return redirect(url_for('dashboard.test_configs'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error deleting test configuration: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.test_configs'))
