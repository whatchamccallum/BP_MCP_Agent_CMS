"""
Environment views.
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from api.models import db
from api.models.environment import Environment
from .utils import get_current_user, normalize_user_id
from . import dashboard_blueprint

@dashboard_blueprint.route('/environments/check-name', methods=['GET'])
def check_environment_name():
    """Check if an environment name already exists."""
    name = request.args.get('name')
    env_id = request.args.get('id')
    
    if not name:
        return jsonify({'valid': False, 'message': 'Environment name is required'})
    
    query = Environment.query.filter(Environment.name == name)
    if env_id:
        # If updating, exclude the current environment from the check
        query = query.filter(Environment.id != int(env_id))
    
    exists = query.first() is not None
    
    return jsonify({
        'valid': not exists,
        'message': f'An environment with the name "{name}" already exists' if exists else ''
    })

@dashboard_blueprint.route('/environments')
def environments():
    """Environments page."""
    # Get environments
    environments = Environment.query.all()
    
    return render_template(
        'dashboard/environments.html',
        environments=environments
    )

@dashboard_blueprint.route('/environments/create', methods=['POST'])
def create_environment():
    """Create a new environment."""
    try:
        # Get current user
        current_user = get_current_user()
        created_by = normalize_user_id(current_user)
        
        name = request.form.get('name')
        ip_address = request.form.get('ip_address')
        port = request.form.get('port')
        username = request.form.get('username')
        password = request.form.get('password')
        is_active = request.form.get('is_active')
        description = request.form.get('description')
        
        if not name or not ip_address or not port or not username or not password:
            flash('All required fields must be filled', 'error')
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            return redirect(url_for('dashboard.environments'))
        
        try:
            port = int(port)
        except ValueError:
            flash('Port must be a valid number', 'error')
            if request.is_json:
                return jsonify({'error': 'Port must be a valid number'}), 400
            return redirect(url_for('dashboard.environments'))
        
        environment = Environment(
            name=name,
            ip_address=ip_address,
            port=port,
            username=username,
            password=password,
            is_active=is_active == 'on',
            description=description,
            created_by=created_by
        )
        
        db.session.add(environment)
        db.session.commit()
        
        flash('Environment created successfully', 'success')
        
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.environments')
            })
        
        return redirect(url_for('dashboard.environments'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error creating environment: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.environments'))

@dashboard_blueprint.route('/environments/<int:id>/update', methods=['POST'])
def update_environment(id):
    """Update an existing environment."""
    try:
        # Get current user
        current_user = get_current_user()
        
        # Get environment
        environment = Environment.query.get_or_404(id)
        
        name = request.form.get('name')
        ip_address = request.form.get('ip_address')
        port = request.form.get('port')
        username = request.form.get('username')
        password = request.form.get('password')
        is_active = request.form.get('is_active')
        description = request.form.get('description')
        
        if not name or not ip_address or not port or not username:
            flash('All required fields must be filled', 'error')
            if request.is_json:
                return jsonify({'error': 'Missing required fields'}), 400
            return redirect(url_for('dashboard.environments'))
        
        try:
            port = int(port)
        except ValueError:
            flash('Port must be a valid number', 'error')
            if request.is_json:
                return jsonify({'error': 'Port must be a valid number'}), 400
            return redirect(url_for('dashboard.environments'))
        
        # Check if name conflicts with another environment
        name_conflict = Environment.query.filter(
            Environment.name == name, 
            Environment.id != id
        ).first()
        
        if name_conflict:
            flash(f'Another environment with the name "{name}" already exists', 'error')
            if request.is_json:
                return jsonify({'error': f'Another environment with the name "{name}" already exists'}), 400
            return redirect(url_for('dashboard.environments'))
        
        # Update environment
        environment.name = name
        environment.ip_address = ip_address
        environment.port = port
        environment.username = username
        if password:  # Only update password if a new one is provided
            environment.password = password
        environment.is_active = is_active == 'on'
        environment.description = description
        environment.updated_by = normalize_user_id(current_user)
        
        db.session.commit()
        
        flash('Environment updated successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.environments')
            })
        
        return redirect(url_for('dashboard.environments'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating environment: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.environments'))

@dashboard_blueprint.route('/environments/<int:id>/delete', methods=['POST'])
def delete_environment(id):
    """Delete an existing environment."""
    try:
        # Get environment
        environment = Environment.query.get_or_404(id)
        
        # Delete environment
        db.session.delete(environment)
        db.session.commit()
        
        flash('Environment deleted successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.environments')
            })
        
        return redirect(url_for('dashboard.environments'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error deleting environment: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.environments'))
