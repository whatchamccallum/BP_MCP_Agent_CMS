"""
Environment API routes.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from api.models import db
from api.models.environment import Environment

environment_blueprint = Blueprint('environment', __name__)


@environment_blueprint.route('', methods=['GET'])
@jwt_required()
def get_environments():
    """Get all environments."""
    environments = Environment.query.all()
    return jsonify([env.to_dict() for env in environments])


@environment_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_environment(id):
    """Get environment by ID."""
    environment = Environment.query.get_or_404(id)
    return jsonify(environment.to_dict())


@environment_blueprint.route('', methods=['POST'])
@jwt_required()
def create_environment():
    """Create a new environment."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    environment = Environment(
        name=data['name'],
        description=data.get('description'),
        ip_address=data.get('ip_address'),
        port=data.get('port'),
        username=data.get('username'),
        password=data.get('password'),
        is_active=data.get('is_active', True),
        attributes=data.get('attributes'),
        created_by=data.get('created_by')
    )
    
    try:
        db.session.add(environment)
        db.session.commit()
        return jsonify(environment.to_dict()), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Environment with this name already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@environment_blueprint.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_environment(id):
    """Update an environment."""
    environment = Environment.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        environment.name = data['name']
    
    if 'description' in data:
        environment.description = data['description']
    
    if 'ip_address' in data:
        environment.ip_address = data['ip_address']
        
    if 'port' in data:
        environment.port = data['port']
        
    if 'username' in data:
        environment.username = data['username']
        
    if 'password' in data and data['password']:
        environment.password = data['password']
        
    if 'is_active' in data:
        environment.is_active = data['is_active']
    
    if 'attributes' in data:
        environment.attributes = data['attributes']
        
    if 'updated_by' in data:
        environment.updated_by = data['updated_by']
    
    try:
        db.session.commit()
        return jsonify(environment.to_dict())
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Environment with this name already exists'}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@environment_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_environment(id):
    """Delete an environment."""
    environment = Environment.query.get_or_404(id)
    
    try:
        db.session.delete(environment)
        db.session.commit()
        return jsonify({'message': 'Environment deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
