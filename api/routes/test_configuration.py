"""
Test Configuration API routes.
"""

from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import IntegrityError

from api.models import db
from api.models.test_configuration import TestConfiguration
from api.controllers.bp_agent import BPAgentController

test_configuration_blueprint = Blueprint('test_configuration', __name__)


@test_configuration_blueprint.route('', methods=['GET'])
@jwt_required()
def get_test_configurations():
    """Get all test configurations."""
    test_configs = TestConfiguration.query.all()
    return jsonify([config.to_dict() for config in test_configs])


@test_configuration_blueprint.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_test_configuration(id):
    """Get test configuration by ID."""
    test_config = TestConfiguration.query.get_or_404(id)
    return jsonify(test_config.to_dict())


@test_configuration_blueprint.route('', methods=['POST'])
@jwt_required()
def create_test_configuration():
    """Create a new test configuration."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    required_fields = ['name', 'test_type', 'config_data']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    user = get_jwt_identity()
    
    test_config = TestConfiguration(
        name=data['name'],
        description=data.get('description'),
        test_type=data['test_type'],
        bp_test_id=data.get('bp_test_id'),
        config_data=data['config_data'],
        created_by=user
    )
    
    try:
        db.session.add(test_config)
        db.session.commit()
        return jsonify(test_config.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@test_configuration_blueprint.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_test_configuration(id):
    """Update a test configuration."""
    test_config = TestConfiguration.query.get_or_404(id)
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    if 'name' in data:
        test_config.name = data['name']
    
    if 'description' in data:
        test_config.description = data['description']
    
    if 'test_type' in data:
        test_config.test_type = data['test_type']
    
    if 'bp_test_id' in data:
        test_config.bp_test_id = data['bp_test_id']
    
    if 'config_data' in data:
        test_config.config_data = data['config_data']
    
    try:
        db.session.commit()
        return jsonify(test_config.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@test_configuration_blueprint.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_test_configuration(id):
    """Delete a test configuration."""
    test_config = TestConfiguration.query.get_or_404(id)
    
    try:
        db.session.delete(test_config)
        db.session.commit()
        return jsonify({'message': 'Test configuration deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@test_configuration_blueprint.route('/<int:id>/run', methods=['POST'])
@jwt_required()
def run_test_configuration(id):
    """Run a test configuration."""
    test_config = TestConfiguration.query.get_or_404(id)
    data = request.get_json() or {}
    
    # Get environment and device IDs from request
    environment_id = data.get('environment_id')
    device_id = data.get('device_id')
    
    if not environment_id:
        return jsonify({'error': 'environment_id is required'}), 400
    
    if not device_id:
        return jsonify({'error': 'device_id is required'}), 400
    
    # Get current user
    user = get_jwt_identity()
    
    # Create BP Agent controller
    bp_agent = BPAgentController(current_app)
    
    try:
        # Run the test
        test_run = bp_agent.run_test(
            test_config=test_config,
            environment_id=environment_id,
            device_id=device_id,
            created_by=user
        )
        
        return jsonify(test_run.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
