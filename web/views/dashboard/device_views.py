"""
Device views.
"""
from flask import render_template, redirect, url_for, request, flash, jsonify
from api.models import db
from api.models.device import Device
from .utils import validate_ip_address
from . import dashboard_blueprint

@dashboard_blueprint.route('/devices/check-name', methods=['GET'])
def check_device_name():
    """Check if a device name already exists."""
    name = request.args.get('name')
    device_id = request.args.get('id')
    
    if not name:
        return jsonify({'valid': False, 'message': 'Device name is required'})
    
    query = Device.query.filter(Device.name == name)
    if device_id:
        # If updating, exclude the current device from the check
        query = query.filter(Device.id != int(device_id))
    
    exists = query.first() is not None
    
    return jsonify({
        'valid': not exists,
        'message': f'A device with the name "{name}" already exists' if exists else ''
    })

@dashboard_blueprint.route('/devices')
def devices():
    """Devices page."""
    # Get devices
    devices = Device.query.all()
    
    return render_template(
        'dashboard/devices.html',
        devices=devices
    )

@dashboard_blueprint.route('/devices/create', methods=['POST'])
def create_device():
    """Create a new device."""
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    device_type = request.form.get('device_type')
    model = request.form.get('model')
    is_active = request.form.get('is_active')
    description = request.form.get('description')
    
    # Validation
    errors = []
    if not name:
        errors.append('Device name is required')
    elif len(name) > 100:
        errors.append('Device name must be 100 characters or less')
    
    if not ip_address:
        errors.append('IP Address is required')
    elif not validate_ip_address(ip_address):
        errors.append('Invalid IP Address format')
    
    if not device_type:
        errors.append('Device Type is required')
    
    # Check if a device with the same name already exists
    existing_device = Device.query.filter_by(name=name).first()
    if existing_device:
        errors.append(f'A device with the name "{name}" already exists')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        
        if request.is_json:
            return jsonify({'error': errors}), 400
        return redirect(url_for('dashboard.devices'))
    
    try:
        # Store model and is_active in attributes JSON field
        attributes = {}
        if model:
            attributes['model'] = model
        if is_active is not None:
            attributes['is_active'] = is_active == 'on'
        
        device = Device(
            name=name,
            ip_address=ip_address,
            type=device_type,
            description=description,
            attributes=attributes
        )
        
        db.session.add(device)
        db.session.commit()
        
        flash('Device created successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.devices')
            })
        
        return redirect(url_for('dashboard.devices'))
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error creating device: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.devices'))

@dashboard_blueprint.route('/devices/<int:id>/update', methods=['POST'])
def update_device(id):
    """Update an existing device."""
    # Get device
    device = Device.query.get_or_404(id)
    
    name = request.form.get('name')
    ip_address = request.form.get('ip_address')
    device_type = request.form.get('device_type')
    model = request.form.get('model')
    is_active = request.form.get('is_active')
    description = request.form.get('description')
    
    # Validation
    errors = []
    if not name:
        errors.append('Device name is required')
    elif len(name) > 100:
        errors.append('Device name must be 100 characters or less')
    
    if not ip_address:
        errors.append('IP Address is required')
    elif not validate_ip_address(ip_address):
        errors.append('Invalid IP Address format')
    
    if not device_type:
        errors.append('Device Type is required')
    
    # Check if another device with the same name already exists
    name_conflict = Device.query.filter(Device.name == name, Device.id != id).first()
    if name_conflict:
        errors.append(f'Another device with the name "{name}" already exists')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        
        if request.is_json:
            return jsonify({'error': errors}), 400
        return redirect(url_for('dashboard.devices'))
    
    try:
        # Update device
        device.name = name
        device.ip_address = ip_address
        device.type = device_type
        
        # Store model and is_active in attributes JSON field
        attributes = device.attributes or {}
        if model:
            attributes['model'] = model
        if is_active is not None:
            attributes['is_active'] = is_active == 'on'
        device.attributes = attributes
        
        device.description = description
        
        db.session.commit()
        
        flash('Device updated successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.devices')
            })
        
        return redirect(url_for('dashboard.devices'))
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating device: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.devices'))

@dashboard_blueprint.route('/devices/<int:id>/delete', methods=['POST'])
def delete_device(id):
    """Delete an existing device."""
    try:
        # Get device
        device = Device.query.get_or_404(id)
        
        # Delete device
        db.session.delete(device)
        db.session.commit()
        
        flash('Device deleted successfully', 'success')
        
        if request.is_json:
            return jsonify({
                'success': True,
                'redirect': url_for('dashboard.devices')
            })
        
        return redirect(url_for('dashboard.devices'))
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error deleting device: {str(e)}"
        flash(error_msg, 'error')
        
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        return redirect(url_for('dashboard.devices'))
