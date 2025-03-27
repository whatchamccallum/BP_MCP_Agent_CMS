"""
Device API routes.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from api.models import db
from api.models.device import Device

device_blueprint = Blueprint('device', __name__)


@device_blueprint.route('', methods=['GET'])
@jwt_required()
def get_devices():
    """Get all devices."""
    devices = Device.query.all()
    return jsonify([device.to_dict() for device in devices])


@device_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_device(id):
    """Get device by ID."""
    device = Device.query.get_or_404(id)
    return jsonify(device.to_dict())


@device_blueprint.route('', methods=['POST'])
@jwt_required()
def create_device():
    """Create a new device."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'type']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    device = Device(
        name=data['name'],
        description=data.get('description'),
        type=data['type'],
        ip_address=data.get('ip_address'),
        credentials=data.get('credentials'),
        attributes=data.get('attributes')
    )
    
    try:
        db.session.add(device)
        db.session.commit()
        return jsonify(device.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Device with this name already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@device_blueprint.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_device(id):
    """Update a device."""
    device = Device.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        device.name = data['name']
    
    if 'description' in data:
        device.description = data['description']
    
    if 'type' in data:
        device.type = data['type']
    
    if 'ip_address' in data:
        device.ip_address = data['ip_address']
    
    if 'credentials' in data:
        device.credentials = data['credentials']
    
    if 'attributes' in data:
        device.attributes = data['attributes']
    
    try:
        db.session.commit()
        return jsonify(device.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Device with this name already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@device_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_device(id):
    """Delete a device."""
    device = Device.query.get_or_404(id)
    
    try:
        db.session.delete(device)
        db.session.commit()
        return jsonify({'message': 'Device deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
